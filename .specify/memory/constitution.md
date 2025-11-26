# Computer Vision Research Project Constitution

## Core Principles

### I. Simplicity & Clarity (NON-NEGOTIABLE)
Code must be simple, readable, and maintainable.
- Prefer clear, explicit code over clever abstractions
- Use descriptive variable names (e.g., `train_dataloader`, not `tdl`)
- Follow PyTorch conventions and idioms
- No unnecessary complexity or premature optimization
- Document complex algorithms or non-obvious design decisions
- Keep functions focused - one responsibility per function (under 50 lines preferred)
- **No tests required** - Focus on experimentation, not test coverage (personal research context)

### II. Reproducibility First (NON-NEGOTIABLE)
Every experiment must be reproducible.
- Set random seeds (Python, NumPy, PyTorch, CUDA) at the start of every script
- Version all datasets with clear documentation of preprocessing steps
- Track all hyperparameters in MLflow
- Log model architecture, training configuration, and environment details
- Use requirements.txt or environment.yml for dependency management
- Document data sources and acquisition methods

### III. Experiment Tracking
All experiments MUST be logged to MLflow.
- Log hyperparameters: learning rate, batch size, optimizer settings, etc.
- Log metrics: train/val loss, accuracy, IoU, mAP (task-specific)
- Log artifacts: model checkpoints, confusion matrices, sample predictions
- Use meaningful experiment names and tags for easy filtering
- Track dataset versions and splits used
- Include training time and resource usage

### IV. Data Pipeline Standards
Data handling must be clean and efficient.
- Use PyTorch DataLoader with proper num_workers for your system
- Implement data augmentation through torchvision.transforms or albumentations
- Separate data loading logic from model training logic
- Cache preprocessed data when beneficial
- Document image sizes, normalization values, and augmentation strategies
- Use lazy loading for large datasets

### V. Model Development
Follow PyTorch best practices.
- Models as `nn.Module` classes with clear forward() methods
- Use `torch.nn.functional` for operations without learnable parameters
- Leverage pretrained models from torchvision.models when appropriate (transfer learning)
- **Open source & free models only** - No API keys, no paid services. Use models from torchvision, timm, HuggingFace (free tier), or other open source repositories
- Save full model state (model, optimizer, epoch, metrics) in checkpoints
- Use `.to(device)` properly - define device once, use consistently
- Implement proper train/eval mode switching

### VI. Cost Efficiency (NON-NEGOTIABLE)
Minimize or eliminate all costs.
- Prototype and debug locally before using cloud GPUs
- Use spot/preemptible instances when possible
- Monitor and log resource usage (GPU memory, training time)
- Clean up resources immediately after experiments
- Consider model size vs performance trade-offs
- Use mixed precision training (AMP) when appropriate for speed/memory savings
- **Zero-cost requirement**: No API keys, no paid model services, no paid datasets. Everything must be free and open source.

### VII. Visual Validation
Trust but verify with visualization.
- Visualize training curves (loss, metrics) for every experiment
- Save sample predictions periodically during training
- Visualize data augmentation pipeline on sample images
- Create confusion matrices or visualization appropriate to task (classification, detection, segmentation)
- Review failure cases - where does the model perform poorly?

## Technical Standards

### Environment & Dependencies
- Python 3.9+ required
- PyTorch 2.0+ with CUDA support (if GPU available)
- MLflow for experiment tracking
- torchvision for CV utilities and pretrained models
- **All dependencies must be free and open source** - No paid libraries or services
- Use requirements.txt or conda environment.yml for reproducibility

### Model & Data Sources (NON-NEGOTIABLE)
- **Open source models only**: torchvision.models, timm, HuggingFace (free tier), PyTorch Hub, or other freely available repositories
- **No API keys required**: All models must be downloadable and runnable locally without authentication
- **Free datasets only**: Use public datasets (ImageNet, COCO, CelebA, etc.) or custom collected data
- **No paid services**: No OpenAI, Anthropic, commercial APIs, or paid model hosting

### Code Quality
- Follow PEP 8 style guidelines (use black formatter recommended)
- Use type hints for function signatures
- Keep functions under 50 lines when possible
- Use docstrings for non-obvious functions
- Comment "why" not "what" - code should be self-documenting
- **No tests required** - This is a personal research project focused on experimentation and iteration, not production deployment. Code validation happens through experiment results and visual inspection.

### Hyperparameter Management
- Store hyperparameters in config files (YAML/JSON) not hardcoded
- Use argparse for command-line overrides
- Log all hyperparameters to MLflow automatically
- Keep a log of what you've tried and what worked

### Computer Vision Specifics
- Use ImageNet normalization unless domain-specific requirements exist
- Start with pretrained models (transfer learning) when applicable - **only from free sources** (torchvision, timm, HuggingFace)
- Apply appropriate data augmentation for task
- Handle class imbalance if present (weighted loss, sampling strategies)
- Use appropriate loss functions for task (CrossEntropy, BCE, MSE, focal loss, etc.)

## Development Workflow

### Experiment Lifecycle
1. **Setup**: Define hypothesis, select baseline architecture, prepare data
2. **Implementation**: Write clean, simple code following PyTorch patterns
3. **Logging**: Configure MLflow experiment with descriptive name and tags
4. **Training**: Run experiment with full tracking (seeds, params, metrics)
5. **Analysis**: Review results, visualizations, compare with baselines
6. **Iteration**: Document findings, adjust approach, repeat

### Checkpointing Strategy
- Save checkpoints after each epoch to separate files
- Keep best model based on validation metric
- Keep last N checkpoints for recovery
- Include optimizer state for resumable training
- Name checkpoints descriptively: `model_epoch10_val-acc0.85.pth`

### Resource Management
- Profile code if performance is unexpectedly slow
- Use DataLoader with pin_memory=True for GPU training
- Consider gradient accumulation for large models with limited GPU memory
- Use torch.compile() for PyTorch 2.0+ speed improvements

## Governance

This constitution supersedes convenience and "just this once" shortcuts.

### Non-Negotiable Requirements
- Every experiment MUST have reproducible setup (seed + config)
- Every model training MUST be logged to MLflow
- Code simplicity is mandatory - refactor complex code immediately
- No principle can be skipped without explicit constitution amendment
- **Zero-cost mandate**: No paid services, APIs, or models under any circumstances

### Complexity Justification
- New dependencies must have clear benefit over existing tools
- Abstractions must simplify, not obscure
- If in doubt, choose the simpler approach

### Amendment Process
- Amendments require updating this document with rationale
- Version must increment following semantic versioning
- Breaking changes require MAJOR version bump
- New principles/sections require MINOR version bump
- Clarifications/refinements require PATCH version bump

### When Stuck
- Review similar papers/repos for inspiration
- Prototype in notebook, refactor to script when working
- Start with smallest possible dataset/model to debug
- Ask: "What's the simplest thing that could work?"

**Version**: 1.0.0 | **Ratified**: 2025-11-26 | **Last Amended**: 2025-11-26
