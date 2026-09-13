# Optional model experiment — not executed

The serving app does not need a fine-tuned model. Its baseline routes a few structured feeling/context labels to reviewed optional actions. A learned router is worth considering only if independently reviewed preference data shows a meaningful benefit over those rules.

Do not train a stress detector on the existing authored cases, and do not claim their contract labels are physiological ground truth. Do not use private journal text or raw Watch measurements for a language-model training dataset.

For a later Week 5 experiment, collect consented, reviewed, de-identified **preference** examples containing only feeling/context enums, eligible actions, the user's selected action, and an anonymous episode group. Split by person/episode before augmentation (for example 60/20/20); reserve an additional independently authored adversarial set. Compare local rules, the frozen hosted base model and a LoRA adapter on action validity, preference agreement, abstention, user burden, latency and cost. Respect fluid/movement constraints outside the model regardless of accuracy.

The following example LLaMA-Factory configuration is a recipe only. Model availability, license, tokenizer, template and current provider deployment support must be checked before execution. The dataset is deliberately not supplied because no independently reviewed preference dataset exists yet. Training requires a separately provisioned compatible GPU environment and an explicit cost decision; none was provisioned here.
