# -*- coding: utf-8 -*-
"""Lab3 Gesture Recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w_dvlMDYMNxvZRdftlmaORgRBhqQSEI5

# Lab 3: Gesture Recognition using Convolutional Neural Networks

In this lab you will train a convolutional neural network to make classifications on different hand gestures. By the end of the lab, you should be able to:

1. Load and split data for training, validation and testing
2. Train a Convolutional Neural Network
3. Apply transfer learning to improve your model

Note that for this lab we will not be providing you with any starter code. You should be able to take the code used in previous labs, tutorials and lectures and modify it accordingly to complete the tasks outlined below.

### What to submit

Submit a PDF file containing all your code, outputs, and write-up
from parts 1-5. You can produce a PDF of your Google Colab file by
going to **File > Print** and then save as PDF. The Colab instructions
has more information. Make sure to review the PDF submission to ensure that your answers are easy to read. Make sure that your text is not cut off at the margins.

**Do not submit any other files produced by your code.**

Include a link to your colab file in your submission.

Please use Google Colab to complete this assignment. If you want to use Jupyter Notebook, please complete the assignment and upload your Jupyter Notebook file to Google Colab for submission.

## Colab Link

Include a link to your colab file here

Colab Link: https://colab.research.google.com/drive/1w_dvlMDYMNxvZRdftlmaORgRBhqQSEI5?usp=sharing

## Dataset

American Sign Language (ASL) is a complete, complex language that employs signs made by moving the
hands combined with facial expressions and postures of the body. It is the primary language of many
North Americans who are deaf and is one of several communication options used by people who are deaf or
hard-of-hearing. The hand gestures representing English alphabet are shown below. This lab focuses on classifying a subset
of these hand gesture images using convolutional neural networks. Specifically, given an image of a hand
showing one of the letters A-I, we want to detect which letter is being represented.

![alt text](https://www.disabled-world.com/pics/1/asl-alphabet.jpg)

## Part B. Building a CNN [50 pt]

For this lab, we are not going to give you any starter code. You will be writing a convolutional neural network
from scratch. You are welcome to use any code from previous labs, lectures and tutorials. You should also
write your own code.

You may use the PyTorch documentation freely. You might also find online tutorials helpful. However, all
code that you submit must be your own.

Make sure that your code is vectorized, and does not contain obvious inefficiencies (for example, unecessary
for loops, or unnecessary calls to unsqueeze()). Ensure enough comments are included in the code so that
your TA can understand what you are doing. It is your responsibility to show that you understand what you
write.

**This is much more challenging and time-consuming than the previous labs.** Make sure that you
give yourself plenty of time by starting early.

### 1. Data Loading and Splitting [5 pt]

Download the anonymized data provided on Quercus. To allow you to get a heads start on this project we will provide you with sample data from previous years. Split the data into training, validation, and test sets.

Note: Data splitting is not as trivial in this lab. We want our test set to closely resemble the setting in which
our model will be used. In particular, our test set should contain hands that are never seen in training!

Explain how you split the data, either by describing what you did, or by showing the code that you used.
Justify your choice of splitting strategy. How many training, validation, and test images do you have?

For loading the data, you can use plt.imread as in Lab 1, or any other method that you choose. You may find
torchvision.datasets.ImageFolder helpful. (see https://pytorch.org/docs/stable/torchvision/datasets.html?highlight=image%20folder#torchvision.datasets.ImageFolder
)
"""

import torch
import os
import time
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import torch.optim as optim
import torchvision
from torchvision.datasets import ImageFolder
from collections import defaultdict
from torchvision import datasets, transforms
from torch.utils.data import TensorDataset,DataLoader, SubsetRandomSampler

from google.colab import drive
drive.mount('/content/gdrive')

def print_folder_structure(directory):
    """Count the number of images in each class folder."""
    total = 0
    count_list = []
    for folder in sorted(os.listdir(directory)):
        count = 0  # Initialize count to 0 for each folder
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):  # Check if the item is a directory
            count = 0
            for _ in os.listdir(folder_path):
                count += 1
        print(f"{folder}: {count}")
        total += count
        count_list.append(count)
    print(f"Total: {total}")
    return count_list

# Define the data transformation including normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Load the dataset
data_folder = datasets.ImageFolder\
 ('/content/gdrive/MyDrive/Lab3_Gestures_Summer', transform=transform)

# Count the number of images in each class folder
count_list = print_folder_structure\
 ('/content/gdrive/MyDrive/Lab3_Gestures_Summer')

# Create a dictionary to hold indices for each unique subject
subject_dict = defaultdict(list)

# Group the image indices by their subject IDs
for idx, (path, _) in enumerate(data_folder.imgs):
    filename = os.path.basename(path)
    subject_id = filename.split('_')[0]
    subject_dict[subject_id].append(idx)

# Shuffle the subject IDs
subject_ids = list(subject_dict.keys())
np.random.shuffle(subject_ids)

# Split the subject IDs into training, validation, and test sets(70-15-15 split)
train_subject_ids = subject_ids[:int(len(subject_ids) * 0.7)]
val_subject_ids = subject_ids[int(len(subject_ids) * 0.7):\
                              int(len(subject_ids) * 0.85)]
test_subject_ids = subject_ids[int(len(subject_ids) * 0.85):]

# Get the corresponding indices for each dataset
train_indices = [idx for subject in train_subject_ids \
                 for idx in subject_dict[subject]]
val_indices = [idx for subject in val_subject_ids \
               for idx in subject_dict[subject]]
test_indices = [idx for subject in test_subject_ids \
                for idx in subject_dict[subject]]

# Shuffle the training indices to randomize the training set
np.random.shuffle(train_indices)

# Create DataLoader objects using SubsetRandomSampler
train_sampler = SubsetRandomSampler(train_indices)
val_sampler = SubsetRandomSampler(val_indices)
test_sampler = SubsetRandomSampler(test_indices)

train_loader = DataLoader(data_folder, batch_size=32, sampler=train_sampler)
val_loader = DataLoader(data_folder, batch_size=32, sampler=val_sampler)
test_loader = DataLoader(data_folder, batch_size=32, sampler=test_sampler)

# Print the number of images in each set
print(f"Number of training images: {len(train_indices)}")
print(f"Number of validation images: {len(val_indices)}")
print(f"Number of test images: {len(test_indices)}")

"""The data was split based on unique subject IDs to ensure that the test set contains hands that are never seen in training, adhering to the requirement for a realistic evaluation of the model. Specifically, the filenames of the images were parsed to extract subject IDs, which were then grouped. These unique subject IDs were randomly shuffled and split into training, validation, and test sets, following a 70-15-15 percentage split.

This strategy ensures that all images of a specific hand (subject) are either in the training, validation, or test set, but never in more than one. This simulates a more realistic scenario where the model is tested on completely unseen data.

The total number of images is 2219. Among these, 1553 images are allocated for training, 333 for validation, and 333 for testing.

### 2. Model Building and Sanity Checking [15 pt]

### Part (a) Convolutional Network - 5 pt

Build a convolutional neural network model that takes the (224x224 RGB) image as input, and predicts the gesture
letter. Your model should be a subclass of nn.Module. Explain your choice of neural network architecture: how
many layers did you choose? What types of layers did you use? Were they fully-connected or convolutional?
What about other decisions like pooling layers, activation functions, number of channels / hidden units?
"""

class GestureCNN(nn.Module):
    def __init__(self):
        super(GestureCNN, self).__init__()
        self.name = "GestureCNN"
        # Input: 3 channels, Output: 16 channels, Kernel: 3x3
        self.conv1 = nn.Conv2d(3, 16, 3)
        # Input: 16 channels, Output: 32 channels, Kernel: 3x3
        self.conv2 = nn.Conv2d(16, 32, 3)
        # Input: 32 channels, Output: 64 channels, Kernel: 3x3
        self.conv3 = nn.Conv2d(32, 64, 3)

        self.pool = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(64 * 26 * 26, 128)
        # 9 classes for the 9 different gestures
        self.fc2 = nn.Linear(128, 9)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 64 * 26 * 26)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

"""The proposed CNN architecture consists of three convolutional layers with 16, 32, and 64 channels, each followed by a max-pooling layer with a 2x2 window. ReLU activation is used after each layer, except the output layer. The network ends with two fully connected layers, the first having 128 hidden units and the second having 9 units corresponding to the number of classes. This architecture aims to balance feature learning and computational efficiency, making it suitable for the given dataset size.

### Part (b) Training Code - 5 pt

Write code that trains your neural network given some training data. Your training code should make it easy
to tweak the usual hyperparameters, like batch size, learning rate, and the model object itself. Make sure
that you are checkpointing your models from time to time (the frequency is up to you). Explain your choice
of loss function and optimizer.
"""

# Function to generate a model name based on hyperparameters
def get_model_name(name, batch_size, learning_rate, epoch):
    return f"model_{name}_bs{batch_size}_lr{learning_rate}_epoch{epoch}"

# Function for training the model
def train(model, train_loader, val_loader, batch_size=64, \
          learning_rate=0.01, num_epochs=1):
    # Set the random seed for reproducibility
    torch.manual_seed(1000)

    # Use CrossEntropyLoss as the loss function
    criterion = nn.CrossEntropyLoss()

    # Use SGD with momentum as the optimizer
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    # Initialize lists to store loss and accuracy values
    train_losses, avg_train_losses, val_losses, train_acc, val_acc \
    = [], [], [], [], []

    # Initialize variable for the number of iterations
    n = 0

    # Measure the time taken for training
    start_time = time.time()

    for epoch in range(num_epochs):
        epoch_acc = 0  # Initialize epoch accuracy to 0
        num_batches = 0  # Initialize the number of batches to 0
        for imgs, labels in train_loader:
            # Move tensors to GPU if CUDA is available
            if torch.cuda.is_available():
                imgs, labels = imgs.cuda(), labels.cuda()

            # Forward pass
            outputs = model(imgs)
            loss = criterion(outputs, labels)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            # Record the training loss
            train_losses.append(float(loss) / batch_size)

            # Calculate training accuracy for the batch and accumulate
            _, pred_labels = torch.max(outputs, dim=1)
            epoch_acc += (pred_labels == labels).float().mean().item()

            num_batches += 1  # Increase the count of processed batches

        # Calculate the mean epoch accuracy
        if num_batches > 0:
            epoch_acc /= num_batches  # Average over all batches

        train_acc.append(epoch_acc)  # Append the epoch-wise training accuracy

        # Calculate average training loss for the epoch
        avg_train_loss = sum(train_losses[-num_batches:]) / num_batches
        avg_train_losses.append(avg_train_loss)

        # Validation loop
        val_loss = 0
        correct = 0
        total = 0
        for imgs, labels in val_loader:
            if torch.cuda.is_available():
                imgs, labels = imgs.cuda(), labels.cuda()
            outputs = model(imgs)
            val_loss += criterion(outputs, labels).item()
            _, pred_labels = torch.max(outputs, dim=1)
            correct += (pred_labels == labels).sum().item()
            total += imgs.shape[0]

        val_accuracy = correct / total  # Calculate validation accuracy
        val_losses.append(float(val_loss) / total)
        val_acc.append(val_accuracy)

        print(f"Epoch: {epoch} Training Accuracy: {epoch_acc} \
        Validation Accuracy: {val_accuracy}")

        # Save the model
        model_path = get_model_name(model.name, batch_size, learning_rate, \
                                    epoch)
        torch.save(model.state_dict(), model_path)

    # Calculate the time taken for training
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

    # Plotting the average training and validation loss
    plt.figure()
    plt.title("Average Training and Validation Loss per Epoch")
    plt.plot(avg_train_losses, label="Average Training Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.show()

    # Plotting the training and validation accuracy
    plt.figure()
    plt.title("Training and Validation Accuracy")
    plt.plot(train_acc, label="Training Accuracy")
    plt.plot(val_acc, label="Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.show()

    print(f"Final Training Accuracy: {train_acc[-1]}")
    print(f"Final Validation Accuracy: {val_acc[-1]}")

"""I chose the CrossEntropyLoss function because it's well-suited for classification problems, especially when the classes are mutually exclusive, as in this case of gesture recognition. For the optimizer, I used Stochastic Gradient Descent (SGD) with momentum. SGD is a widely-used optimizer that's computationally efficient, and adding momentum helps the optimizer navigate along the relevant directions and smoothen the optimization landscape, which usually leads to faster convergence.

### Part (c) “Overfit” to a Small Dataset - 5 pt

One way to sanity check our neural network model and training code is to check whether the model is capable
of “overfitting” or “memorizing” a small dataset. A properly constructed CNN with correct training code
should be able to memorize the answers to a small number of images quickly.

Construct a small dataset (e.g. just the images that you have collected). Then show that your model and
training code is capable of memorizing the labels of this small data set.

With a large batch size (e.g. the entire small dataset) and learning rate that is not too high, You should be
able to obtain a 100% training accuracy on that small dataset relatively quickly (within 200 iterations).
"""

# Initialize model
model = GestureCNN()
model.name = "GestureCNN"

# Check if CUDA is available and if so, move the model to GPU memory
if torch.cuda.is_available():
    model = model.cuda()
    print(f"CUDA is available. Model moved to: \
    {next(model.parameters()).device}")
else:
    print("CUDA is not available. Model running on CPU.")

# Define the path to your small_data directory
small_data_directory = "/content/gdrive/MyDrive/small_data"

# Count the number of images in each class folder
count_list_small = print_folder_structure(small_data_directory)

# Load the small dataset
small_data_folder = ImageFolder(small_data_directory, transform=transform)

# Create a dictionary to hold indices for each unique subject in the small dataset
subject_dict_small = defaultdict(list)

# Group the image indices by their subject IDs
for idx, (path, _) in enumerate(small_data_folder.imgs):
    filename = os.path.basename(path)
    subject_id = filename.split('_')[0]
    subject_dict_small[subject_id].append(idx)

# Shuffle the subject IDs
subject_ids_small = list(subject_dict_small.keys())
np.random.shuffle(subject_ids_small)

# Split the subject IDs into training and validation sets (80-20 split)
train_subject_ids_small = subject_ids_small[:int(len(subject_ids_small) * 0.8)]
val_subject_ids_small = subject_ids_small[int(len(subject_ids_small) * 0.8):]

# Get the corresponding indices for each dataset
train_indices_small = [idx for subject in train_subject_ids_small \
                       for idx in subject_dict_small[subject]]
val_indices_small = [idx for subject in val_subject_ids_small \
                     for idx in subject_dict_small[subject]]

# Create DataLoader objects using SubsetRandomSampler
train_sampler_small = SubsetRandomSampler(train_indices_small)
val_sampler_small = SubsetRandomSampler(val_indices_small)

small_train_loader = DataLoader(small_data_folder, \
batch_size=len(train_indices_small), sampler=train_sampler_small)
small_val_loader = DataLoader(small_data_folder, \
batch_size=len(val_indices_small), sampler=val_sampler_small)

# Train the model on the small dataset
train(model, small_train_loader, small_val_loader, \
batch_size=len(train_indices_small), learning_rate=0.01, num_epochs=200)

"""My small_data consists of 45 images. Training accuracy reaches 100% at epoch 36. While validation accuracy is much lower, confirming overfitting. The GPU accelerates the process, completing 200 epochs in 60.82 seconds.

### 3. Hyperparameter Search [10 pt]

### Part (a) - 1 pt

List 3 hyperparameters that you think are most worth tuning. Choose at least one hyperparameter related to
the model architecture.

1. Learning Rate: Affects the convergence and stability of the model during training.

2. Batch Size: Impacts the gradient estimate and training speed.

3. Number of Epochs: Determines the number of times the model is exposed to the training set, affecting underfitting or overfitting.

### Part (b) - 5 pt

Tune the hyperparameters you listed in Part (a), trying as many values as you need to until you feel satisfied
that you are getting a good model. Plot the training curve of at least 4 different hyperparameter settings.
"""

cnn_1 = GestureCNN()
if torch.cuda.is_available():
  cnn_1.cuda()
  print('Training on GPU')
else:
  print('Training on CPU')

train(cnn_1, train_loader, val_loader, batch_size=32, \
      learning_rate=0.01, num_epochs=10)

cnn_2 = GestureCNN()
if torch.cuda.is_available():
    cnn_2.cuda()
    print('Training on GPU')
else:
    print('Training on CPU')

train(cnn_2, train_loader, val_loader, batch_size=64, \
      learning_rate=0.005, num_epochs=20)

cnn_3 = GestureCNN()
if torch.cuda.is_available():
    cnn_3.cuda()
    print('Training on GPU')
else:
    print('Training on CPU')

train(cnn_3, train_loader, val_loader, batch_size=32, \
      learning_rate=0.005, num_epochs=15)

cnn_4 = GestureCNN()
if torch.cuda.is_available():
  cnn_4.cuda()
  print('Training on GPU')
else:
  print('Training on CPU')

train(cnn_4, train_loader, val_loader, batch_size=24, \
      learning_rate=0.005, num_epochs=12)

"""### Part (c) - 2 pt
Choose the best model out of all the ones that you have trained. Justify your choice.

The best model is the third model with a batch size of 32, number of epochs 15, and a learning rate of 0.005. I choose this model because it not only achieves the highest validation accuracy of approximately 79.3% but also maintains a high training accuracy of approximately 98.0%. This model represents a good balance between performance and overfitting, as evidenced by the high validation accuracy.

### Part (d) - 2 pt
Report the test accuracy of your best model. You should only do this step once and prior to this step you should have only used the training and validation data.
"""

# Function to evaluate the model on the test set
def evaluate(model, test_loader):
    model.eval()  # Set the model to evaluation mode
    correct = 0
    total = 0

    with torch.no_grad():  # No need to calculate gradients
        for imgs, labels in test_loader:
            if torch.cuda.is_available():
                imgs, labels = imgs.cuda(), labels.cuda()

            outputs = model(imgs)
            _, pred_labels = torch.max(outputs, dim=1)
            correct += (pred_labels == labels).sum().item()
            total += imgs.shape[0]

    test_accuracy = correct / total
    return test_accuracy

test_accuracy = evaluate(cnn_3, test_loader)
print(f"Test Accuracy: {test_accuracy}")

"""### 4. Transfer Learning [15 pt]
For many image classification tasks, it is generally not a good idea to train a very large deep neural network
model from scratch due to the enormous compute requirements and lack of sufficient amounts of training
data.

One of the better options is to try using an existing model that performs a similar task to the one you need
to solve. This method of utilizing a pre-trained network for other similar tasks is broadly termed **Transfer
Learning**. In this assignment, we will use Transfer Learning to extract features from the hand gesture
images. Then, train a smaller network to use these features as input and classify the hand gestures.

As you have learned from the CNN lecture, convolution layers extract various features from the images which
get utilized by the fully connected layers for correct classification. AlexNet architecture played a pivotal
role in establishing Deep Neural Nets as a go-to tool for image classification problems and we will use an
ImageNet pre-trained AlexNet model to extract features in this assignment.

### Part (a) - 5 pt
Here is the code to load the AlexNet network, with pretrained weights. When you first run the code, PyTorch
will download the pretrained weights from the internet.
"""

import torchvision.models
alexnet = torchvision.models.alexnet(pretrained=True)

"""The alexnet model is split up into two components: *alexnet.features* and *alexnet.classifier*. The
first neural network component, *alexnet.features*, is used to compute convolutional features, which are
taken as input in *alexnet.classifier*.

The neural network alexnet.features expects an image tensor of shape Nx3x224x224 as input and it will
output a tensor of shape Nx256x6x6 . (N = batch size).

Compute the AlexNet features for each of your training, validation, and test data. Here is an example code
snippet showing how you can compute the AlexNet features for some images (your actual code might be
different):
"""

# img = ... a PyTorch tensor with shape [N,3,224,224] containing hand images ...
# features = alexnet.features(img)

"""**Save the computed features**. You will be using these features as input to your neural network in Part
(b), and you do not want to re-compute the features every time. Instead, run *alexnet.features* once for
each image, and save the result.
"""

def compute_save_features(data_loader, name):
    all_features = []
    all_labels = []

    for i, (imgs, labels) in enumerate(data_loader):
        print(f"Batch {i+1}")
        if torch.cuda.is_available():
            imgs, labels = imgs.cuda(), labels.cuda()
            alexnet.cuda()

        features = alexnet.features(imgs)

        all_features.append(features.cpu().detach().numpy())
        all_labels.append(labels.cpu().numpy())

    all_features = np.concatenate(all_features, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    np.save(f"{name}_features.npy", all_features)
    np.save(f"{name}_labels.npy", all_labels)

compute_save_features(train_loader, "train")
compute_save_features(val_loader, "val")
compute_save_features(test_loader, "test")

"""### Part (b) - 3 pt
Build a convolutional neural network model that takes as input these AlexNet features, and makes a
prediction. Your model should be a subclass of nn.Module.

Explain your choice of neural network architecture: how many layers did you choose? What types of layers
did you use: fully-connected or convolutional? What about other decisions like pooling layers, activation
functions, number of channels / hidden units in each layer?

Here is an example of how your model may be called:
"""

class New_Model(nn.Module):
    def __init__(self, num_classes=9):
        super(New_Model, self).__init__()
        # Fully-connected layer with 512 hidden units
        self.fc1 = nn.Linear(256 * 6 * 6, 512)
        # Fully-connected layer with 128 hidden units
        self.fc2 = nn.Linear(512, 128)
        # Output layer
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten the tensor
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

"""The architecture employs three fully-connected layers, with the first two layers followed by ReLU activation functions. The use of ReLU aims to introduce non-linearity while mitigating the vanishing gradient problem. The choice of 512 and 128 hidden units for the first and second layers aims to capture complex relationships in the AlexNet features without overfitting. The model is designed for classification based on high-level features from AlexNet, thus obviating the need for additional convolutional or pooling layers.

### Part (c) - 5 pt
Train your new network, including any hyperparameter tuning. Plot and submit the training curve of your
best model only.

Note: Depending on how you are caching (saving) your AlexNet features, PyTorch might still be tracking
updates to the **AlexNet weights**, which we are not tuning. One workaround is to convert your AlexNet
feature tensor into a numpy array, and then back into a PyTorch tensor.
"""

# tensor = torch.from_numpy(tensor.detach().numpy())

# Load saved features
train_features = torch.tensor(np.load("train_features.npy"))
train_labels = torch.tensor(np.load("train_labels.npy"))
val_features = torch.tensor(np.load("val_features.npy"))
val_labels = torch.tensor(np.load("val_labels.npy"))

# Create PyTorch Datasets
train_dataset = TensorDataset(train_features, train_labels)
val_dataset = TensorDataset(val_features, val_labels)

# Create PyTorch DataLoaders
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

# Initialize your model, loss function, and optimizer
model = New_Model(num_classes=9)
if torch.cuda.is_available():
    model = model.cuda()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
train_accuracies, val_accuracies = [], []  # Initialize lists to store accuracies
train_losses, val_losses = [], []  # Initialize lists to store losses

for epoch in range(10):
    model.train()
    train_loss = 0
    correct_train = 0
    total_train = 0

    for features, labels in train_loader:
        if torch.cuda.is_available():
            features, labels = features.cuda(), labels.cuda()
        optimizer.zero_grad()
        output = model(features)
        loss = criterion(output, labels)
        train_loss += loss.item()
        loss.backward()
        optimizer.step()

        # Compute training accuracy
        _, predicted = torch.max(output.data, 1)
        total_train += labels.size(0)
        correct_train += (predicted == labels).sum().item()

    train_accuracy = correct_train / total_train
    train_accuracies.append(train_accuracy)
    train_losses.append(train_loss / len(train_loader))

    # Validation step
    model.eval()
    val_loss = 0
    correct_val = 0
    total_val = 0

    with torch.no_grad():
        for features, labels in val_loader:
            if torch.cuda.is_available():
                features, labels = features.cuda(), labels.cuda()
            output = model(features)
            val_loss += criterion(output, labels).item()

            # Compute validation accuracy
            _, predicted = torch.max(output.data, 1)
            total_val += labels.size(0)
            correct_val += (predicted == labels).sum().item()

    val_accuracy = correct_val / total_val
    val_accuracies.append(val_accuracy)
    val_losses.append(val_loss / len(val_loader))

    print(f"Epoch {epoch+1}, Training Accuracy: {train_accuracy}, \
    Validation Accuracy: {val_accuracy}")

# First plot for loss
plt.figure(figsize=(6, 4))
plt.plot(train_losses, label='Training Loss')
plt.plot(val_losses, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('Loss Curve')
plt.show()

# Second plot for accuracy
plt.figure(figsize=(6, 4))
plt.plot(train_accuracies, label='Training Accuracy')
plt.plot(val_accuracies, label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Accuracy Curve')
plt.show()

"""### Part (d) - 2 pt
Report the test accuracy of your best model. How does the test accuracy compare to Part 3(d) without transfer learning?
"""

def evaluate_with_alexnet_features(model, test_loader):
    model.eval()  # Set the model to evaluation mode
    correct = 0
    total = 0

    with torch.no_grad():  # No need to calculate gradients
        for features, labels in test_loader:
            if torch.cuda.is_available():
                features, labels = features.cuda(), labels.cuda()

            outputs = model(features)
            _, pred_labels = torch.max(outputs, dim=1)
            correct += (pred_labels == labels).sum().item()
            total += features.shape[0]

    test_accuracy = correct / total
    return test_accuracy

test_features = torch.tensor(np.load("test_features.npy"))
test_labels = torch.tensor(np.load("test_labels.npy"))

# Create a DataLoader for the test set
test_dataset = TensorDataset(test_features, test_labels)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Evaluate the model
test_accuracy_with_alexnet = evaluate_with_alexnet_features(model, test_loader)
print(f"Test Accuracy with AlexNet features: {test_accuracy_with_alexnet}")

"""The test accuracy with AlexNet features is significantly higher than without transfer learning (0.9339 vs 0.7508 (from Part 3(d))). This demonstrates the power of using pretrained models for feature extraction in improving the performance of the neural network.

### 5. Additional Testing [5 pt]
As a final step in testing we will be revisiting the sample images that you had collected and submitted at the start of this lab. These sample images should be untouched and will be used to demonstrate how well your model works at identifying your hand guestures.

Using the best transfer learning model developed in Part 4. Report the test accuracy on your sample images and how it compares to the test accuracy obtained in Part 4(d)? How well did your model do for the different hand guestures? Provide an explanation for why you think your model performed the way it did?
"""

compute_save_features(small_train_loader, "small_train_features")
compute_save_features(small_val_loader, "small_val_features")

small_train_features = torch.tensor(np.load("small_train_features_features.npy"))
small_train_labels = torch.tensor(np.load("small_train_features_labels.npy"))
small_val_features = torch.tensor(np.load("small_val_features_features.npy"))
small_val_labels = torch.tensor(np.load("small_val_features_labels.npy"))

# Load the pre-computed features and labels for the small dataset's validation set
small_val_features = torch.tensor(np.load("small_val_features_features.npy"))
small_val_labels = torch.tensor(np.load("small_val_features_labels.npy"))

# Initialize your best model from Part 4
best_model = New_Model(num_classes=9)
if torch.cuda.is_available():
    best_model = best_model.cuda()

# Compute accuracy on small dataset (using the validation set as a test set)
correct = 0
total = len(small_val_labels)

for features, labels in zip(small_val_features, small_val_labels):
    if torch.cuda.is_available():
        features, labels = features.cuda(), labels.cuda()
    output = best_model(features.unsqueeze(0))
    _, predicted = torch.max(output.data, 1)
    correct += (predicted == labels).sum().item()

small_test_accuracy = correct / total
print(f"Test Accuracy on small dataset: {small_test_accuracy}")

# Compare with test accuracy from Part 4(d)
print(f"Test Accuracy with AlexNet features: 0.933933933933934")

"""The test accuracy on the small dataset was 0.3333, which is significantly lower than the 0.9339 achieved with AlexNet features on the larger dataset. The model performed poorly on the small dataset for different hand gestures. The likely reason for this lower performance is the limited amount of data in the small dataset, which is insufficient for the model to generalize well. This is in contrast to the larger dataset where the model had more examples to learn from, resulting in a higher test accuracy."""

# Commented out IPython magic to ensure Python compatibility.
# %%shell
# jupyter nbconvert --to html /Lab3_Gesture_Recognition.ipynb