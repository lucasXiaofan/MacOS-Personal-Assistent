# Training-Free Group Relative Policy Optimization

## Paper Details
- **Title**: Training-Free Group Relative Policy Optimization
- **Submitted**: 9 Oct 2025
- **Category**: Computer Science > Computation and Language
- **arXiv ID**: 2510.08191

## Authors
Yuzheng Cai, Siqi Cai, Yuchen Shi, Zihan Xu, Lichao Chen, Yulei Qin, Xiaoyu Tan, Gang Li, Zongyi Li, Haojia Lin, Yong Mao, Ke Li, Xing Sun

## URLs
- **arXiv**: https://arxiv.org/abs/2510.08191
- **HTML Version**: https://arxiv.org/html/2510.08191v1
- **Hugging Face Papers**: https://huggingface.co/papers/2510.08191
- **PDF**: https://arxiv.org/pdf/2510.08191
- **GitHub**: Not yet found (⚠️ needs verification)

## Summary
Training-Free GRPO proposes a cost-effective solution to enhance LLM agent performance **without parameter updates**. The method leverages group relative semantic advantage instead of numerical ones, iteratively distilling high-quality experiential knowledge during multi-epoch learning on minimal ground-truth data. This knowledge serves as a learned token prior integrated during LLM API calls to guide model behavior.

### Key Innovation
- **Problem**: LLM agents struggle with specialized domains due to integration challenges with external tools and prompting strategies
- **Previous Approach**: Supervised Fine-Tuning (SFT) + Reinforcement Learning (RL) with GRPO (expensive parameter updates)
- **New Approach**: Learn experiential knowledge as token prior (lightweight, avoids overfitting)

### Results
- Applied to DeepSeek-V3.1-Terminus on mathematical reasoning and web searching tasks
- Outperforms fine-tuned small LLMs with just a few dozen training samples
- Significantly improves out-of-domain performance

## Keywords
Training-Free GRPO, Group Relative Policy Optimization, Large Language Model, Reinforcement Learning, Output Distribution, Experiential Knowledge, Token Prior, Multi-epoch Learning, Semantic Advantage

## Status
⏳ Awaiting user review | ⚠️ GitHub repository needs verification
