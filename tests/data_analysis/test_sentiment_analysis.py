"""
Tests for sentiment analysis functionality.
"""
import unittest
from unittest.mock import patch, MagicMock

from tumkwe_invest.data_analysis.sentiment_analysis import SentimentAnalyzer


class TestSentimentAnalysis(unittest.TestCase):
    """Test case for sentiment analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample news articles for testing
        self.sample_news_articles = [
            {
                'title': 'Company XYZ reports positive earnings',
                'content': 'The earnings were 20% better than expected for the quarter.'
            },
            {
                'title': 'Market outlook remains neutral',
                'content': 'Analysts expect sideways movement in the coming months.'
            },
            {
                'title': 'Negative economic indicators concern investors',
                'content': 'Inflation and unemployment numbers paint a concerning picture.'
            }
        ]
        
        # Create sample social media posts for testing
        self.sample_social_posts = [
            {'content': 'I just bought more $XYZ stock! Very positive about its future!'},
            {'content': 'Not sure how to feel about the market today. Mixed signals.'},
            {'content': 'Selling all my holdings. This market is too negative for me.'}
        ]
        
    def test_preprocess_text(self):
        """Test text preprocessing functionality."""
        analyzer = SentimentAnalyzer(model_type="nltk")
        
        # Test URL removal
        text = "Check out https://example.com and www.test.com for more info."
        processed = analyzer.preprocess_text(text)
        self.assertNotIn("https://example.com", processed)
        self.assertNotIn("www.test.com", processed)
        
        # Test HTML removal
        text = "<p>This is <b>HTML</b> content</p>"
        processed = analyzer.preprocess_text(text)
        self.assertNotIn("<p>", processed)
        self.assertNotIn("<b>", processed)
        
        # Test case normalization
        text = "MiXeD CaSe TeXt"
        processed = analyzer.preprocess_text(text)
        self.assertEqual(processed, "mixed case text")
        
        # Test special character handling
        text = "Text with $pecial ch@racters!"
        processed = analyzer.preprocess_text(text)
        self.assertIn("$", processed)  # Financial symbols should be kept
        self.assertIn("!", processed)  # Punctuation important for sentiment should be kept
        self.assertNotIn("@", processed)  # Other special chars removed

    @patch('nltk.download')
    def test_analyze_text_nltk(self, mock_download):
        """Test NLTK sentiment analysis."""
        # Mock VADER to return predictable results
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.SentimentIntensityAnalyzer') as mock_sia:
            vader_instance = MagicMock()
            vader_instance.polarity_scores.side_effect = lambda text: {
                'pos': 0.8, 'neg': 0.0, 'neu': 0.2, 'compound': 0.8
            } if 'positive' in text.lower() else (
                {'pos': 0.0, 'neg': 0.8, 'neu': 0.2, 'compound': -0.8} 
                if 'negative' in text.lower() else 
                {'pos': 0.1, 'neg': 0.1, 'neu': 0.8, 'compound': 0.0}
            )
            mock_sia.return_value = vader_instance
            
            analyzer = SentimentAnalyzer(model_type="nltk")
            
            # Test positive sentiment
            result = analyzer.analyze_text("This is a positive statement about the stock market.")
            self.assertEqual(result['sentiment'], 'positive')
            self.assertGreater(result['confidence'], 0.5)
            
            # Test negative sentiment
            result = analyzer.analyze_text("This is a negative outlook for the company.")
            self.assertEqual(result['sentiment'], 'negative')
            self.assertGreater(result['confidence'], 0.5)
            
            # Test neutral sentiment
            result = analyzer.analyze_text("This is a neutral statement.")
            self.assertEqual(result['sentiment'], 'neutral')
            self.assertLessEqual(result['confidence'], 0.5)

    @patch('tumkwe_invest.data_analysis.sentiment_analysis.AutoModelForSequenceClassification')
    @patch('tumkwe_invest.data_analysis.sentiment_analysis.AutoTokenizer')
    def test_analyze_text_huggingface(self, mock_tokenizer, mock_model):
        """Test Hugging Face sentiment analysis."""
        # Configure the mock to avoid actual model loading
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.pipeline') as mock_pipeline:
            pipeline_instance = MagicMock()
            pipeline_instance.side_effect = lambda text: [{
                'label': 'POSITIVE', 'score': 0.9
            }] if 'positive' in text.lower() else (
                [{'label': 'NEGATIVE', 'score': 0.9}] 
                if 'negative' in text.lower() else 
                [{'label': 'NEUTRAL', 'score': 0.9}]
            )
            mock_pipeline.return_value = pipeline_instance
            
            analyzer = SentimentAnalyzer(model_type="huggingface")
            
            # Test positive sentiment
            result = analyzer.analyze_text("This is a positive statement about the stock market.")
            self.assertEqual(result['sentiment'], 'positive')
            
            # Test negative sentiment
            result = analyzer.analyze_text("This is a negative outlook for the company.")
            self.assertEqual(result['sentiment'], 'negative')

    @patch('nltk.download')
    @patch('tumkwe_invest.data_analysis.sentiment_analysis.AutoModelForSequenceClassification')
    @patch('tumkwe_invest.data_analysis.sentiment_analysis.AutoTokenizer')
    def test_analyze_text_ensemble(self, mock_tokenizer, mock_model, mock_download):
        """Test ensemble sentiment analysis."""
        # Mock both VADER and Hugging Face models
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.SentimentIntensityAnalyzer') as mock_sia, \
             patch('tumkwe_invest.data_analysis.sentiment_analysis.pipeline') as mock_pipeline:
            
            # Setup VADER mock
            vader_instance = MagicMock()
            vader_instance.polarity_scores.side_effect = lambda text: {
                'pos': 0.8, 'neg': 0.0, 'neu': 0.2, 'compound': 0.8
            } if 'positive' in text.lower() else (
                {'pos': 0.0, 'neg': 0.8, 'neu': 0.2, 'compound': -0.8} 
                if 'negative' in text.lower() else 
                {'pos': 0.1, 'neg': 0.1, 'neu': 0.8, 'compound': 0.0}
            )
            mock_sia.return_value = vader_instance
            
            # Setup Hugging Face mock
            pipeline_instance = MagicMock()
            pipeline_instance.side_effect = lambda text: [{
                'label': 'POSITIVE', 'score': 0.9
            }] if 'positive' in text.lower() else (
                [{'label': 'NEGATIVE', 'score': 0.9}] 
                if 'negative' in text.lower() else 
                [{'label': 'NEUTRAL', 'score': 0.9}]
            )
            mock_pipeline.return_value = pipeline_instance
            
            analyzer = SentimentAnalyzer(model_type="ensemble")
            
            # Test when both models agree
            result = analyzer.analyze_text("This is a positive statement about the stock market.")
            self.assertEqual(result['sentiment'], 'positive')
            self.assertIn('nltk_result', result)
            self.assertIn('huggingface_result', result)

    def test_analyze_batch(self):
        """Test batch analysis of multiple texts."""
        # Mock VADER for testing
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.SentimentIntensityAnalyzer') as mock_sia:
            vader_instance = MagicMock()
            vader_instance.polarity_scores.side_effect = lambda text: {
                'pos': 0.8, 'neg': 0.0, 'neu': 0.2, 'compound': 0.8
            } if 'positive' in text.lower() else (
                {'pos': 0.0, 'neg': 0.8, 'neu': 0.2, 'compound': -0.8} 
                if 'negative' in text.lower() else 
                {'pos': 0.1, 'neg': 0.1, 'neu': 0.8, 'compound': 0.0}
            )
            mock_sia.return_value = vader_instance
            
            analyzer = SentimentAnalyzer(model_type="nltk")
            
            texts = [
                "This is a positive statement.",
                "This is a negative statement.",
                "This is a neutral statement."
            ]
            
            results = analyzer.analyze_batch(texts)
            
            self.assertEqual(len(results), len(texts))
            self.assertEqual(results[0]['sentiment'], 'positive')
            self.assertEqual(results[1]['sentiment'], 'negative')
            self.assertEqual(results[2]['sentiment'], 'neutral')

    def test_analyze_sources(self):
        """Test analysis of news and social media sources."""
        # Mock VADER for testing
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.SentimentIntensityAnalyzer') as mock_sia:
            vader_instance = MagicMock()
            vader_instance.polarity_scores.side_effect = lambda text: {
                'pos': 0.8, 'neg': 0.0, 'neu': 0.2, 'compound': 0.8
            } if 'positive' in text.lower() else (
                {'pos': 0.0, 'neg': 0.8, 'neu': 0.2, 'compound': -0.8} 
                if 'negative' in text.lower() else 
                {'pos': 0.1, 'neg': 0.1, 'neu': 0.8, 'compound': 0.0}
            )
            mock_sia.return_value = vader_instance
            
            analyzer = SentimentAnalyzer(model_type="nltk")
            
            results = analyzer.analyze_sources(
                news_articles=self.sample_news_articles,
                social_posts=self.sample_social_posts
            )
            
            # Check structure of results
            self.assertIn('news', results)
            self.assertIn('social', results)
            self.assertIn('overall', results)
            
            # Check news analysis
            self.assertEqual(len(results['news']), len(self.sample_news_articles))
            
            # Check social analysis
            self.assertEqual(len(results['social']), len(self.sample_social_posts))
            
            # Check overall analysis
            self.assertIn('dominant_sentiment', results['overall'])
            self.assertIn('confidence', results['overall'])
            self.assertIn('distribution', results['overall'])

    def test_validate_accuracy(self):
        """Test accuracy validation against labeled data."""
        # Mock VADER for testing
        with patch('tumkwe_invest.data_analysis.sentiment_analysis.SentimentIntensityAnalyzer') as mock_sia:
            vader_instance = MagicMock()
            vader_instance.polarity_scores.side_effect = lambda text: {
                'pos': 0.8, 'neg': 0.0, 'neu': 0.2, 'compound': 0.8
            } if 'positive' in text.lower() else (
                {'pos': 0.0, 'neg': 0.8, 'neu': 0.2, 'compound': -0.8} 
                if 'negative' in text.lower() else 
                {'pos': 0.1, 'neg': 0.1, 'neu': 0.8, 'compound': 0.0}
            )
            mock_sia.return_value = vader_instance
            
            analyzer = SentimentAnalyzer(model_type="nltk")
            
            test_data = [
                {"text": "This is a positive statement.", "label": "positive"},
                {"text": "This is a negative statement.", "label": "negative"},
                {"text": "This is a neutral statement.", "label": "neutral"},
                {"text": "This should be positive but model got it wrong.", "label": "positive"}  # Intentional mismatch
            ]
            
            metrics = analyzer.validate_accuracy(test_data)
            
            # Check metrics structure
            self.assertIn('accuracy', metrics)
            self.assertIn('class_metrics', metrics)
            self.assertIn('positive', metrics['class_metrics'])
            self.assertIn('negative', metrics['class_metrics'])
            self.assertIn('neutral', metrics['class_metrics'])
            
            # Check metric components
            for sentiment in ['positive', 'negative', 'neutral']:
                self.assertIn('precision', metrics['class_metrics'][sentiment])
                self.assertIn('recall', metrics['class_metrics'][sentiment])
                self.assertIn('f1_score', metrics['class_metrics'][sentiment])


if __name__ == '__main__':
    unittest.main()
