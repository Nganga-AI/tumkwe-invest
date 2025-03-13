"""
Sentiment analysis module for analyzing news and social media content.

Implements NLP techniques to gauge market sentiment about stocks.
"""

import re
from typing import Any, Dict, List, Optional

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)


class SentimentAnalyzer:
    """
    Analyzes sentiment from news articles and social media posts.
    """

    def __init__(self, model_type: str = "nltk"):
        """
        Initialize sentiment analyzer with specified model type.

        Args:
            model_type (str): Type of model to use ('nltk', 'huggingface', or 'ensemble')
        """
        self.model_type = model_type
        self.results = {}

        # Initialize NLTK
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon")

        # Initialize models based on type
        if model_type in ["nltk", "ensemble"]:
            self.nltk_analyzer = SentimentIntensityAnalyzer()

        if model_type in ["huggingface", "ensemble"]:
            # Use a financial sentiment model if available
            try:
                model_name = "ProsusAI/finbert"
                self.hf_model = AutoModelForSequenceClassification.from_pretrained(
                    model_name
                )
                self.hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.hf_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.hf_model,
                    tokenizer=self.hf_tokenizer,
                )
            except Exception:
                # Fallback to default sentiment model
                self.hf_pipeline = pipeline("sentiment-analysis")

    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis.

        Args:
            text (str): Raw text input

        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"https?://\S+|www\.\S+", "", text)

        # Remove HTML tags
        text = re.sub(r"<.*?>", "", text)

        # Remove special characters but keep punctuation important for sentiment
        text = re.sub(r"[^a-zA-Z0-9\s\.,!?\'\"$%]", "", text)

        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def analyze_text_nltk(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using NLTK's VADER.

        Args:
            text (str): Preprocessed text

        Returns:
            Dict: Sentiment scores
        """
        scores = self.nltk_analyzer.polarity_scores(text)

        # Map compound score to sentiment category
        if scores["compound"] >= 0.05:
            sentiment = "positive"
        elif scores["compound"] <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "scores": scores,
            "sentiment": sentiment,
            "confidence": abs(scores["compound"]),
        }

    def analyze_text_huggingface(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Hugging Face transformers.

        Args:
            text (str): Preprocessed text

        Returns:
            Dict: Sentiment prediction and confidence
        """
        # Truncate text if too long (depends on model limits)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]

        result = self.hf_pipeline(text)[0]

        return {
            "sentiment": result["label"].lower(),
            "confidence": result["score"],
            "scores": {"score": result["score"]},
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text using the configured model.

        Args:
            text (str): Text to analyze

        Returns:
            Dict: Sentiment analysis results
        """
        preprocessed_text = self.preprocess_text(text)

        if self.model_type == "nltk":
            return self.analyze_text_nltk(preprocessed_text)

        elif self.model_type == "huggingface":
            return self.analyze_text_huggingface(preprocessed_text)

        elif self.model_type == "ensemble":
            # Combine results from both models
            nltk_result = self.analyze_text_nltk(preprocessed_text)
            hf_result = self.analyze_text_huggingface(preprocessed_text)

            # Simple voting ensemble
            if nltk_result["sentiment"] == hf_result["sentiment"]:
                sentiment = nltk_result["sentiment"]
                confidence = (nltk_result["confidence"] + hf_result["confidence"]) / 2
            else:
                # If conflicting, choose the one with higher confidence
                if nltk_result["confidence"] > hf_result["confidence"]:
                    sentiment = nltk_result["sentiment"]
                    confidence = nltk_result["confidence"]
                else:
                    sentiment = hf_result["sentiment"]
                    confidence = hf_result["confidence"]

            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "nltk_result": nltk_result,
                "huggingface_result": hf_result,
            }

        return {"error": "Invalid model type"}

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for a batch of texts.

        Args:
            texts (List[str]): List of texts to analyze

        Returns:
            List[Dict]: Sentiment analysis results for each text
        """
        results = []
        for text in texts:
            results.append(self.analyze_text(text))
        return results

    def analyze_sources(
        self, news_articles: List[Dict], social_posts: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment from multiple sources and aggregate results.

        Args:
            news_articles (List[Dict]): List of news articles with 'title' and 'content' fields
            social_posts (List[Dict], optional): List of social media posts with 'content' field

        Returns:
            Dict: Aggregated sentiment analysis results
        """
        all_results = {"news": [], "social": [], "overall": {}}

        # Analyze news articles
        for article in news_articles:
            # Title often carries stronger sentiment signals in news
            title_result = self.analyze_text(article["title"])

            # Content provides more context
            content_result = self.analyze_text(article["content"])

            # Combine title and content results (title given higher weight)
            combined_sentiment = (
                title_result["sentiment"]
                if title_result["confidence"] > content_result["confidence"]
                else content_result["sentiment"]
            )

            article_result = {
                "title": article["title"],
                "title_sentiment": title_result["sentiment"],
                "content_sentiment": content_result["sentiment"],
                "combined_sentiment": combined_sentiment,
                "confidence": (title_result["confidence"] * 0.6)
                + (content_result["confidence"] * 0.4),
            }
            all_results["news"].append(article_result)

        # Analyze social media posts if provided
        if social_posts:
            for post in social_posts:
                post_result = self.analyze_text(post["content"])
                all_results["social"].append(
                    {
                        "content": post["content"],
                        "sentiment": post_result["sentiment"],
                        "confidence": post_result["confidence"],
                    }
                )

        # Aggregate results
        all_sentiments = []
        for source in ["news", "social"]:
            for item in all_results[source]:
                sentiment_key = (
                    "combined_sentiment" if source == "news" else "sentiment"
                )
                if sentiment_key in item:
                    all_sentiments.append(
                        {
                            "sentiment": item[sentiment_key],
                            "confidence": item["confidence"],
                            "source": source,
                        }
                    )

        # Count sentiments
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

        weighted_scores = {"positive": 0, "neutral": 0, "negative": 0}

        for item in all_sentiments:
            sentiment_counts[item["sentiment"]] += 1
            weighted_scores[item["sentiment"]] += item["confidence"]

        # Calculate overall sentiment
        total_items = len(all_sentiments)
        if total_items > 0:
            dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]

            # Calculate average confidence for the dominant sentiment
            avg_confidence = 0
            if sentiment_counts[dominant_sentiment] > 0:
                avg_confidence = (
                    weighted_scores[dominant_sentiment]
                    / sentiment_counts[dominant_sentiment]
                )

            all_results["overall"] = {
                "dominant_sentiment": dominant_sentiment,
                "confidence": avg_confidence,
                "distribution": {
                    "positive_percent": (sentiment_counts["positive"] / total_items)
                    * 100,
                    "neutral_percent": (sentiment_counts["neutral"] / total_items)
                    * 100,
                    "negative_percent": (sentiment_counts["negative"] / total_items)
                    * 100,
                },
            }

        self.results = all_results
        return all_results

    def validate_accuracy(self, test_data: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Validate sentiment accuracy against labeled test data.

        Args:
            test_data (List[Dict]): List of {"text": "...", "label": "positive/negative/neutral"} items

        Returns:
            Dict: Accuracy metrics
        """
        correct = 0
        total = len(test_data)

        confusion_matrix = {
            "true_positive": 0,
            "false_positive": 0,
            "true_negative": 0,
            "false_negative": 0,
            "true_neutral": 0,
            "false_neutral": 0,
        }

        for item in test_data:
            result = self.analyze_text(item["text"])
            predicted = result["sentiment"]
            actual = item["label"]

            if predicted == actual:
                correct += 1
                confusion_matrix[f"true_{actual}"] += 1
            else:
                confusion_matrix[f"false_{predicted}"] += 1

        accuracy = correct / total if total > 0 else 0

        # Calculate precision, recall for each class
        metrics = {"accuracy": accuracy, "class_metrics": {}}

        for sentiment in ["positive", "negative", "neutral"]:
            true_pos = confusion_matrix[f"true_{sentiment}"]
            false_pos_sum = 0
            for other_sentiment in ["positive", "negative", "neutral"]:
                if other_sentiment != sentiment:
                    false_pos_sum += confusion_matrix[f"false_{sentiment}"]

            precision = (
                true_pos / (true_pos + false_pos_sum)
                if (true_pos + false_pos_sum) > 0
                else 0
            )

            # For recall, need to know total actual positives
            actual_sum = true_pos
            for other_sentiment in ["positive", "negative", "neutral"]:
                if other_sentiment != sentiment:
                    actual_sum += confusion_matrix[f"false_{other_sentiment}"]

            recall = true_pos / actual_sum if actual_sum > 0 else 0

            f1 = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0
            )

            metrics["class_metrics"][sentiment] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }

        return metrics
