# Copyright (c) OpenMMLab. All rights reserved.
from .base import INPUT_MODELS
from .llama_awq import LlamaAwqReader, ensure_fp16orint32
from .qwen import Qwen2Model, QwenModel, QwenReader


class QwenAwqReader(QwenReader):
    """QwenAwqReader."""

    def __init__(self, new_params: dict, unused_params: dict, last_bin: bool,
                 model_cfg: dict):
        super().__init__(new_params, unused_params, last_bin, model_cfg)

    def attn(self, i: int):
        """Get q, k, v, o qweight for layer i."""
        return ensure_fp16orint32(self._attn(i, 'qweight', -1, -1))

    def attn_bias(self, i: int):
        """Get q, k, v, o bias for layer i."""
        return ensure_fp16orint32(self._attn(i, 'bias', -1, 0))

    def attn_zero(self, i: int):
        """Get q, k, v, o qzeros for layer i."""
        return ensure_fp16orint32(self._attn(i, 'qzeros', -1, -1))

    def attn_scale(self, i: int):
        """Get q, k, v, o scales for layer i."""
        return ensure_fp16orint32(self._attn(i, 'scales', -1, -1))

    def ffn(self, i: int):
        """Get ffn qweight for layer i."""
        # ours: w2(silu(w1(x)) * w3(x))
        # qwen: c_proj(w1(x) * silu(w2(x)))
        return ensure_fp16orint32(self._ffn(i, 'qweight'))

    def ffn_zero(self, i: int):
        """Get ffn qzeros for layer i."""
        return ensure_fp16orint32(self._ffn(i, 'qzeros'))

    def ffn_scale(self, i: int):
        """Get ffn scales for layer i."""
        return ensure_fp16orint32(self._ffn(i, 'scales'))


@INPUT_MODELS.register_module(name='qwen-awq')
class QwenAwqModel(QwenModel):
    """Qwen awq model in hf format."""

    Reader = QwenAwqReader

    def __init__(self,
                 model_path: str,
                 tokenizer_path: str,
                 ckpt_path: str = None,
                 **kwargs):
        super().__init__(model_path,
                         tokenizer_path,
                         ckpt_path=ckpt_path,
                         **kwargs)


class Qwen2AwqReader(LlamaAwqReader):
    """read qwen2 awq model weights."""

    def __init__(self, new_params: dict, unused_params: dict, last_bin: bool,
                 model_cfg: dict):
        super().__init__(new_params, unused_params, last_bin, model_cfg)

    def attn_bias(self, i: int):
        """Get q, k, v, o bias for layer i."""
        result = []

        for key in ['q', 'k', 'v']:
            tensor = self.params.get(
                f'model.layers.{i}.self_attn.{key}_proj.bias')
            assert tensor is not None
            result.append(tensor)

        ref_tensor = result[0]
        dummy_oproj_bias = ref_tensor.new_zeros(ref_tensor.shape)
        result.append(dummy_oproj_bias)
        return ensure_fp16orint32(result)


@INPUT_MODELS.register_module(name='qwen2-awq')
class Qwen2AwqModel(Qwen2Model):
    """Qwen2 awq model in hf format."""

    Reader = Qwen2AwqReader

    def __init__(self,
                 model_path: str,
                 tokenizer_path: str,
                 ckpt_path: str = None,
                 **kwargs):
        super().__init__(model_path,
                         tokenizer_path,
                         ckpt_path=ckpt_path,
                         **kwargs)
