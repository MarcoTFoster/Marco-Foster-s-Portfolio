# -*- coding: utf-8 -*-
"""Fake_News.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Jou54o1PwYCM75Xgrt3TamuFXd3vHZUU

## **NAIVE BAYS CLASSIFIEER FOR FAKE NEWS RECOGNITON**

Marco Foster & Savina Tsichli
"""

#Project

"""*Fake news are defined by the New York Times as ”a made-up story with an intention to deceive”, with
the intent to confuse or deceive people. They are everywhere in our daily life and they come especially
from social media platforms and applications in the online world. Being able to distinguish fake
contents form real news is today one of the most serious challenges facing the news industry. Naive
Bayes classifiers are powerful algorithms that are used for text data analysis and are connected to
classification tasks of text in multiple classes. The goal of the project is to implement a Multinomial
Naive Bayes classifier in R and test its performances in the classification of social media posts.*
"""

#Instroduction

"""## Dataset 1: Kaggle Multiclass Fake News Dataset
The Kaggle dataset contains 6 possible labels:
- True (5)
- Not-Known (4)
- Mostly-True (3)
- Half-True (2)
- False (1)
- Barely-True (0)

## Dataset 2: Binary Dataset
This dataset contains two labels:
- Reliable (0)
- Unreliable (1)

## Preprocessing

To prepare the data for classification, we employ the following steps:

### Tokenization
We split the text into individual tokens. Tokenization simplifies analysis by focusing on each word as a separate unit.

### Stopword Removal
Stopwords are common words like "and" or "the" that add little semantic value to the text. Removing them allows the model to focus on more important words.


"""

#Objective

"""The purpose of this project is to classify news articles into multiple categories (ranging from "False" to "True") using a **Naive Bayes classifier**. By analyzing the text in news articles, we aim to detect their factuality based on predefined labels. The dataset is split into training, validation, and test sets, and we follow standard text preprocessing techniques, including tokenization, stopword removal, and normalization.

"""

#Naive Bayes Classifier

"""A **Naive Bayes classifier** is a probabilistic machine learning model used for classification tasks. It is based on Bayes' Theorem, assuming independence between features. Despite this "naive" assumption, it performs well in real-world applications, especially for text classification, such as spam detection or sentiment analysis. The algorithm computes the probability of each class given a feature and selects the class with the highest likelihood. It is efficient, easy to implement, and works well with large datasets."""

#Code

# Load Packages
package <- c("tokenizers", "tidytext", "dplyr", "tm", "SnowballC", "e1071", "caret", "readr")
install.packages(package)
install.packages("data.table")

library(tokenizers)
library(tidytext)
library(dplyr)
library(tm)
library(SnowballC)
library(e1071)
library(caret)
library(readr)
library(data.table)

"""**Model Training (Binary Classification)**

After preparing the second dataset, a Naive Bayes model was trained using the training data.
The data was split into training (85%) and validation (15%) sets.
The laplace smoothing parameter was set to `1` to handle the zero probabilities of unseen words in the validation set.
"""

df <- read_csv("train.csv")
test <- read_csv("test.csv")

index <- nrow(df) * 0.85
train <- df[1:index, ]
val <- df[(index + 1):nrow(df), ]

print(nrow(test))
print(nrow(df))
print(nrow(train))
print(nrow(val))

# Extract the Labels and Text columns
y <- train$Labels
Text <- train[["Text"]]

# Tokenize the text and store tokens in a list
tokens_list <- lapply(Text, tokenize_words)
#print(head(tokens_list))

# Extract the Labels and Text columns
train_y <- factor(y, levels = c(0, 1, 2, 3, 4, 5))
val_y <- factor(val$Labels, levels = c(0, 1, 2, 3, 4, 5))

TrainText <- train[["Text"]]
ValText <- val[["Text"]]
TestText <- test[["Text"]]

# Tokenize the text and store tokens in a list
tokens_train <- lapply(TrainText, tokenize_words)
tokens_train <- lapply(tokens_train, function(x) setdiff(x, stopwords("en")))

tokens_val <- lapply(ValText, tokenize_words)
tokens_val <- lapply(tokens_val, function(x) setdiff(x, stopwords("en")))

tokens_test <- lapply(TestText, tokenize_words)
tokens_test <- lapply(tokens_test, function(x) setdiff(x, stopwords("en")))

###
#print(head(tokens_train))
#print(head(tokens_val))
#print(head(tokens_test))

# Create a text corpus for each set
trainCorpus <- Corpus(VectorSource(tokens_train))
valCorpus <- Corpus(VectorSource(tokens_val))
testCorpus <- Corpus(VectorSource(tokens_test))

# Create document-term matrices
train_dtm <- DocumentTermMatrix(trainCorpus)
train_dtm <- removeSparseTerms(train_dtm, 0.95)
val_dtm <- DocumentTermMatrix(valCorpus, control = list(dictionary = Terms(train_dtm)))
test_dtm <- DocumentTermMatrix(testCorpus, control = list(dictionary = Terms(train_dtm)))

# Reduce the number of features in your DTMs
# Try removing sparse terms
#train_dtm <- removeSparseTerms(train_dtm, 0.99) # Keep terms that appear in at least 1% of documents
#val_dtm <- removeSparseTerms(val_dtm, 0.99)
#test_dtm <- removeSparseTerms(test_dtm, 0.99)

"""**Prepare Data for Modeling**"""

# Convert DTMs to Matrices for easier manipulation
train_matrix <- as.matrix(train_dtm)
val_matrix <- as.matrix(val_dtm)
test_matrix <- as.matrix(test_dtm)

# Matrix columns to factors for categorization
for (cols in colnames(train_matrix)) {
  train_matrix[, cols] <- factor(train_matrix[, cols])
}

for (cols in colnames(val_matrix)) {
  val_matrix[, cols] <- factor(val_matrix[, cols])
}

for (cols in colnames(test_matrix)) {
  test_matrix[, cols] <- factor(test_matrix[, cols])
}

# Ensure Labels column is a factor with the correct levels
train$Labels <- factor(train$Labels, levels = c(0, 1, 2, 3, 4, 5))
val$Labels <- factor(val$Labels, levels = c(0, 1, 2, 3, 4, 5))

# Combine Labels and DTM matrix in a data frame
# The labels are combined with the training and validation matrices to prepare for model training.
train_matrix <- data.frame(Labels = train$Labels, train_matrix)
val_matrix <- data.frame(Labels = val$Labels, val_matrix)

#Train the Multinomial Naive Bayes classifier
model <- naiveBayes(Labels ~ ., data = train_matrix)

# Predict on validation set
valPred <- predict(model, newdata = val_matrix)

# Convert predictions and true labels to factors with the same levels
all_levels <- c(0, 1, 2, 3, 4, 5)
valPred <- factor(valPred, levels = all_levels)
val_matrix$Labels <- factor(val_matrix$Labels, levels = all_levels)

# Evaluate the model
cm <- confusionMatrix(valPred, val_matrix$Labels)
print(cm)

# Predict on test set
#testPred <- predict(model, newdata = test_final)

# Ensure test predictions have the same factor levels (optional, depending on use case)
#testPred <- factor(testPred, levels = all_levels)

# Output test predictions
#print(testPred)

"""**Final dataset**

"""

package <- c("tokenizers", "tidytext", "dplyr", "tm", "SnowballC", "e1071", "caret", "readr")
install.packages(package)
install.packages("data.table")

library(tokenizers)
library(tidytext)
library(dplyr)
library(tm)
library(SnowballC)
library(e1071)
library(caret)
library(readr)
library(data.table)

# Same work on new dataset

df <- read_csv("train2.csv")
test <- read_csv("test2.csv")

index <- nrow(df) * 0.85
train <- df[1:index, ]
val <- df[(index + 1):nrow(df), ]

print(nrow(test))
print(nrow(df))
print(nrow(train))
print(nrow(val))

# Extract the Labels and Text columns
y <- train$label
Text <- train[["text"]]

# Tokenize the text and store tokens in a list
tokens_list <- lapply(Text, tokenize_words)
#print(head(tokens_list))

# Extract the Labels and Text columns
train_y <- factor(y, levels = c(0, 1))
val_y <- factor(val$label, levels = c(0, 1))

TrainText <- train[["text"]]
ValText <- val[["text"]]
TestText <- test[["text"]]

# Tokenize the text and store tokens in a list
tokens_train <- lapply(TrainText, tokenize_words)
tokens_train <- lapply(tokens_train, function(x) setdiff(x, stopwords("en")))

tokens_val <- lapply(ValText, tokenize_words)
tokens_val <- lapply(tokens_val, function(x) setdiff(x, stopwords("en")))

tokens_test <- lapply(TestText, tokenize_words)
tokens_test <- lapply(tokens_test, function(x) setdiff(x, stopwords("en")))

###
#print(head(tokens_train))
#print(head(tokens_val))
#print(head(tokens_test))

# Create a text corpus for each set
trainCorpus <- Corpus(VectorSource(tokens_train))
valCorpus <- Corpus(VectorSource(tokens_val))
testCorpus <- Corpus(VectorSource(tokens_test))

# Create document-term matrices
train_dtm <- DocumentTermMatrix(trainCorpus)
train_dtm <- removeSparseTerms(train_dtm, 0.95)
val_dtm <- DocumentTermMatrix(valCorpus, control = list(dictionary = Terms(train_dtm)))
test_dtm <- DocumentTermMatrix(testCorpus, control = list(dictionary = Terms(train_dtm)))

# Reduce the number of features in your DTMs
#train_dtm <- removeSparseTerms(train_dtm, 0.99) # Keep terms that appear in at least 1% of documents
#val_dtm <- removeSparseTerms(val_dtm, 0.99)
#test_dtm <- removeSparseTerms(test_dtm, 0.99)

train_matrix <- as.matrix(train_dtm)
val_matrix <- as.matrix(val_dtm)
test_matrix <- as.matrix(test_dtm)

for (cols in colnames(train_matrix)) {
  train_matrix[, cols] <- factor(train_matrix[, cols])
}

for (cols in colnames(val_matrix)) {
  val_matrix[, cols] <- factor(val_matrix[, cols])
}

for (cols in colnames(test_matrix)) {
  test_matrix[, cols] <- factor(test_matrix[, cols])
}

train_matrix <- data.frame(Labels = as.factor(train$label), train_matrix)
val_matrix <- data.frame(Labels = as.factor(val$label), val_matrix)

all(colnames(train_matrix) == colnames(val_matrix))  # Should return TRUE
all(colnames(train_matrix) == colnames(test_matrix))  # Should return TRUE

train_matrix$Labels

# Train the Multinomial Naive Bayes classifier
model2 <- naiveBayes(Labels ~ ., data = train_matrix, laplace = 1)

# Predict on validation set
valPred2 <- predict(model2, newdata = val_matrix[,-1])

# Convert predictions and true labels to factors with the same levels
all_levels <- c(0, 1)  # Set explicitly for binary classification
valPred2 <- factor(valPred2, levels = all_levels)
val_matrix$Labels <- factor(val_matrix$Labels, levels = all_levels)

# Evaluate the model
cm <- confusionMatrix(valPred2, val_matrix$Labels)
print(cm)

# Predict on test set
#testPred2 <- predict(model2, newdata = test_matrix)

# Ensure test predictions have the same factor levels (optional, depending on use case)
#testPred2 <- factor(testPred2, levels = all_levels)

# Output test predictions
#print(head(testPred2))

"""## **Transformer**

Alternative Approach: Transformers for Fake News Detection

While the Naive Bayes classifier is effective for many text classification tasks, modern approaches using transformer models have demonstrated superior performance. Transformers, such as BERT, utilize embeddings that capture contextual relationships in text, leading to better classification accuracy.

In this section, we propose replacing the Naive Bayes classifier with a transformer-based model for the fake news detection task.
"""

# For this we will need to also install the packages:

install.packages("torch")
install.packages("dplyr")

library(dplyr)
torch::install_torch()
# Install devtools if you don't have it
install.packages("devtools")

# Use devtools to install the package from GitHub
devtools::install_github("huggingface/transformers")

# After loading the datasets, the labels are converted to numeric,
# and then we extract text from both training and test datasets

# Tokenize the data with a pre-trained tokenizer
# This way we convert texts to token IDs with embeddings

tokenizer <- transformers::AutoTokenizer$from_pretrained("bert-base-uncased")

# Then we create a dataset that holds tokenized input and corresponding labels

# After loading the pre-trained model,
# we test it by running the data through it and get predictions.

# then we evaluate the model by comparing the predictions to the actual labels,
# and then calculate accuracy

"""## Summary of Findings

1) We implemented the Naive Bayes Classifier first on a binary dataset (0,1), and then on the Fake News multi-class dataset (0,1,2,3,4,5). Even though the results of the first dataset were expected, the model on the multi-class dataset did not work accurately for the categorization of the news. We explain this by mentioning that:
- the Naive Bayes Classifier Model assumes that features (e.g., words or phrases) are independent given the class label. In this particular example with the news articles, this assumption doesn’t hold. For example, certain phrases may often occur together in genuine articles but not in fake ones.
- The model may not effectively capture the nuances that differentiate the two categories, especially if they share a lot of vocabulary.
- It treats every feature independently and doesn’t consider the context or relationships between words.

2) That lead us to our next step which was to use a model that takes into account the position of a token in a given phrase or sentence. The transformer is a good example of a model that uses Attention, adding embeddings to each token so as to capture semantic meanings, contextual relationships, and positional information.

- By implementing a transformer-based model for fake news detection, we expect improved accuracy and reliability compared to the Naive Bayes classifier. The context-aware nature of transformers enables a deeper understanding of text, which is critical for accurately distinguishing between real and fake news.


"""