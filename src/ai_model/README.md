# AI Model Development for Tanam Rawat

This directory will house the internal AI model development for plant identification.

## Objective
To develop a highly accurate plant identification model specifically trained on Indonesian flora, addressing the limitations of global models.

## Technologies Under Consideration
- **Frameworks:** TensorFlow, PyTorch
- **Libraries:** Keras, scikit-learn, OpenCV

## Initial Data Collection Plan
- Explore publicly available datasets of Indonesian flora.
- Collaborate with local botanical gardens, universities, and plant communities for image collection.
- Implement a crowdsourcing mechanism within the Tanam Rawat app (future phase) to gather user-contributed images.

## Development Phases
1.  **Data Acquisition & Preprocessing:** Gather, clean, and label image datasets.
2.  **Model Selection & Training:** Experiment with various CNN architectures (e.g., ResNet, EfficientNet) and train models.
3.  **Evaluation & Fine-tuning:** Evaluate model performance using relevant metrics (accuracy, precision, recall) and fine-tune as needed.
4.  **Deployment:** Integrate the trained model into the FastAPI backend for inference.
