"""
Tests for the sentiment analysis module of the data analysis package.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from typing import Dict, Any, List

from tumkwe_invest.data_analysis.sentiment_analysis import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample texts for testing
        self.positive_text = "The company reported excellent earnings, exceeding all expectations!"
        self.negative_text = "The stock crashed following poor management decisions and declining sales."
        self.neutral_text = "The market remained stable today with trading volumes at average levels."
        
        # Sample news articles
        self.news_articles = [
            {
                'title': 'Company XYZ reports record profits',
                'content': 'Company XYZ announced today that it has achieved record profits in the last quarter, exceeding analyst expectations.'
            },
            {
                'title': 'Market uncertainty affects stocks',
                'content': 'Increasing uncertainty in global markets has led to volatility in stock prices across various sectors.'
            },
            {
                'title': 'New product launch fails to impress',
                'content': 'The much-anticipated product launch by Company ABC failed to generate excitement among consumers and analysts.'
            }
        ]
        
        # Sample social posts
        self.social_posts = [
            {'content': 'Just bought more shares of $XYZ, feeling bullish!'},
            {'content': 'Not happy with the management decisions at $ABC. Selling my position.'},
            {'content': 'The market seems unpredictable today. Watching from the sidelines.'}
        ]
        
        # Sample test data for model validation
        self.test_data = [
            {"text": "The company's profits increased by 30%", "label": "positive"},
            {"text": "Major layoffs announced, stock tumbling", "label": "negative"},
            {"text": "Company maintains current dividend rate", "label": "neutral"},
            {"text": "Revolutionary new product unveiled today", "label": "positive"},
            {"text": "Regulatory investigation impacts share price", "label": "negative"}
        ]

    @patch('nltk.sentiment.vader.SentimentIntensityAnalyzer')
    def test_initialize_nltk_analyzer(self, mock_nltk_analyzer):
        """Test initialization with NLTK analyzer."""
        # Mock the NLTK analyzer
        mock_instance = MagicMock()
        mock_nltk_analyzer.return_value = mock_instance
        
        # Test initialization with NLTK
        analyzer = SentimentAnalyzer(model_type='nltk')
        
        # Check that NLTK analyzer was initialized
        self.assertEqual(analyzer.model_type, 'nltk')
        self.assertTrue(hasattr(analyzer, 'nltk_analyzer'))

    @patch('nltk.sentiment.vader.SentimentIntensityAnalyzer')
    @patch('transformers.pipeline')
    def test_initialize_ensemble_analyzer(self, mock_pipeline, mock_nltk_analyzer):
        """Test initialization with ensemble analyzer."""
        # Mock the NLTK analyzer and HuggingFace pipeline
        mock_nltk_instance = MagicMock()
        mock_nltk_analyzer.return_value = mock_nltk_instance
        
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Test initialization with ensemble
        with patch('transformers.AutoModelForSequenceClassification.from_pretrained') as mock_model:
            with patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer:
                analyzer = SentimentAnalyzer(model_type='ensemble')
                
                # Check that both analyzers were initialized
                self.assertEqual(analyzer.model_type, 'ensemble')
                self.assertTrue(hasattr(analyzer, 'nltk_analyzer'))
                self.assertTrue(hasattr(analyzer, 'hf_pipeline'))

    def test_preprocess_text(self):
        """Test text preprocessing."""
        # Create analyzer (use NLTK to avoid loading heavy models)
        with patch('nltk.sentiment.vader.SentimentIntensityAnalyzer'):
            analyzer = SentimentAnalyzer(model_type='nltk')
            
            # Test preprocessing
            text = "Check out this link: https://example.com and <b>HTML</b> tags! $$$"
            processed = analyzer.preprocess_text(text)
            
            # Check URL removal
            self.assertNotIn("https://", processed)
            # Check HTML tag removal
            self.assertNotIn("<b>", processed)
            self.assertNotIn("</b>", processed)
            # Check case conversion
            self.assertEqual(processed, processed.lower())
            # Check special character handling
            self.assertNotIn("$$$", processed)

    @patch('nltk.sentiment.vader.SentimentIntensityAnalyzer')
    def test_analyze_text_nltk(self, mock_nltk_analyzer):
        """Test sentiment analysis using NLTK."""
        # Mock NLTK analyzer with predetermined responses
        mock_instance = MagicMock()
        mock_nltk_analyzer.return_value = mock_instance
        
        # Configure mock for different texts
        def polarity_side_effect(text):
            if "excellent" in text.lower():
                return {'neg': 0.0, 'neu': 0.3, 'pos': 0.7, 'compound': 0.8}
            elif "crashed" in text.lower():
                return {'neg': 0.7, 'neu': 0.3, 'pos': 0.0, 'compound': -0.8}
            else:
                return {'neg': 0.1, 'neu': 0.8, 'pos': 0.1, 'compound': 0.0}
        
        mock_instance.polarity_scores.side_effect = polarity_side_effect
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer(model_type='nltk')
        
        # Test positive text
        pos_result = analyzer.analyze_text_nltk(self.positive_text)
        self.assertEqual(pos_result['sentiment'], 'positive')
        self.assertTrue(pos_result['confidence'] > 0.5)
        
        # Test negative text
        neg_result = analyzer.analyze_text_nltk(self.negative_text)
        self.assertEqual(neg_result['sentiment'], 'negative')
        self.assertTrue(neg_result['confidence'] > 0.5)
        
        # Test neutral text
        neu_result = analyzer.analyze_text_nltk(self.neutral_text)
        self.assertEqual(neu_result['sentiment'], 'neutral')

    @patch('transformers.pipeline')
    def test_analyze_text_huggingface(self, mock_pipeline):
        """Test sentiment analysis using Hugging Face."""
        # Configure mock with predetermined responses
        mock_pipeline_instance = MagicMock()
        
        def pipeline_side_effect(text):
            if "excellent" in text.lower():
                return [{'label': 'POSITIVE', 'score': 0.95}]
            elif "crashed" in text.lower():
                return [{'label': 'NEGATIVE', 'score': 0.92}]
            else:
                return [{'label': 'NEUTRAL', 'score': 0.85}]
        
        mock_pipeline_instance.side_effect = pipeline_side_effect
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Initialize analyzer with mocked Hugging Face
        with patch('transformers.AutoModelForSequenceClassification.from_pretrained'):
            with patch('transformers.AutoTokenizer.from_pretrained'):
                analyzer = SentimentAnalyzer(model_type='huggingface')
                
                # Mock the huggingface pipeline method directly
                analyzer.hf_pipeline = mock_pipeline_instance
                
                # Test positive text
                pos_result = analyzer.analyze_text_huggingface(self.positive_text)
                self.assertEqual(pos_result['sentiment'], 'positive')
                self.assertTrue(pos_result['confidence'] > 0.9)
                
                # Test negative text
                neg_result = analyzer.analyze_text_huggingface(self.negative_text)
                self.assertEqual(neg_result['sentiment'], 'negative')
                self.assertTrue(neg_result['confidence'] > 0.9)
                
                # Test neutral text
                neu_result = analyzer.analyze_text_huggingface(self.neutral_text)
                self.assertEqual(neu_result['sentiment'], 'neutral')

    @patch('nltk.sentiment.vader.SentimentIntensityAnalyzer')
    @patch('transformers.pipeline')
    def test_analyze_sources(self, mock_pipeline, mock_nltk_analyzer):
        """Test analysis of multiple sources."""
        # Configure mocks with simple predetermined responses
        mock_nltk_instance = MagicMock()
        mock_nltk_instance.polarity_scores.return_value = {
            'neg': 0.1, 'neu': 0.2, 'pos': 0.7, 'compound': 0.6
        }
        mock_nltk_analyzer.return_value = mock_nltk_instance
        
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = [{'label': 'POSITIVE', 'score': 0.8}]
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Initialize analyzer with ensemble to test both pathways
        with patch('transformers.AutoModelForSequenceClassification.from_pretrained'):
            with patch('transformers.AutoTokenizer.from_pretrained'):
                analyzer = SentimentAnalyzer(model_type='nltk')  # Use NLTK for simplicity
                analyzer.analyze_text = MagicMock()
                
                # Configure analyze_text mock to return different sentiments
                def analyze_side_effect(text):
                    if "record profits" in text.lower() or "bullish" in text.lower():
                        return {'sentiment': 'positive', 'confidence': 0.8}
                    elif "fails" in text.lower() or "not happy" in text.lower():
                        return {'sentiment': 'negative', 'confidence': 0.7}
                    else:
                        return {'sentiment': 'neutral', 'confidence': 0.6}
                
                analyzer.analyze_text.side_effect = analyze_side_effect
                
                # Test analysis of sources
                results = analyzer.analyze_sources(self.news_articles, self.social_posts)
                
                # Check results structure
                self.assertIn('news', results)
                self.assertIn('social', results)
                self.assertIn('overall', results)
                self.assertEqual(len(results['news']), len(self.news_articles))
                self.assertEqual(len(results['social']), len(self.social_posts))
                
                # Check that overall sentiment is calculated
                self.assertIn('dominant_sentiment', results['overall'])
                self.assertIn('confidence', results['overall'])
                self.assertIn('distribution', results['overall'])

    @patch('nltk.sentiment.vader.SentimentIntensityAnalyzer')
    def test_validate_accuracy(self, mock_nltk_analyzer):
        """Test validation of sentiment model accuracy."""
        # Mock NLTK analyzer
        mock_instance = MagicMock()
        mock_nltk_analyzer.return_value = mock_instance
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer(model_type='nltk')
        analyzer.analyze_text = MagicMock()
        
        # Configure analyze_text to match labels 3 out of 5 times
        predictions = [
            {'sentiment': 'positive', 'confidence': 0.8},  # Match
            {'sentiment': 'negative', 'confidence': 0.7},  # Match
            {'sentiment': 'positive', 'confidence': 0.6},  # Mismatch (should be neutral)
            {'sentiment': 'positive', 'confidence': 0.9},  # Match
            {'sentiment': 'neutral', 'confidence': 0.5}    # Mismatch (should be negative)
        ]
        analyzer.analyze_text.side_effect = predictions
        
        # Test validation
        metrics = analyzer.validate_accuracy(self.test_data)
        
        # Check that metrics are calculated
        self.assertIn('accuracy', metrics)
        self.assertIn('class_metrics', metrics)
        self.assertEqual(metrics['accuracy'], 0.6)  # 3/5 correct
        
        # Check class metrics
        for sentiment in ['positive', 'negative', 'neutral']:
            self.assertIn(sentiment, metrics['class_metrics'])
            for metric in ['precision', 'recall', 'f1_score']:
                self.assertIn(metric, metrics['class_metrics'][sentiment])


if __name__ == '__main__':
    unittest.main()
