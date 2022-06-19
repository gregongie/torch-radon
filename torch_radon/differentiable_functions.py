try:
    import torch_radon_cuda
except Exception as e:
    print("Importing exception")

from torch.autograd import Function


class RadonForward(Function):
    @staticmethod
    def forward(ctx, x, angles, tex_cache, rays_cfg):
        sinogram = torch_radon_cuda.forward(x, angles, tex_cache, rays_cfg)
        ctx.tex_cache = tex_cache
        ctx.rays_cfg = rays_cfg
        ctx.save_for_backward(angles)
        ctx.save_for_forward(angles)

        return sinogram

    @staticmethod
    def backward(ctx, grad_x):
        if not grad_x.is_contiguous():
            grad_x = grad_x.contiguous()

        angles, = ctx.saved_variables
        grad = torch_radon_cuda.backward(grad_x, angles, ctx.tex_cache, ctx.rays_cfg)
        return grad, None, None, None

    @staticmethod
    def jvp(ctx, x, arg1, arg2, arg3):
        angles, = ctx.saved_tensors
        sinogram = torch_radon_cuda.forward(x, angles, ctx.tex_cache, ctx.rays_cfg)
        return sinogram

class RadonBackprojection(Function):
    @staticmethod
    def forward(ctx, x, angles, tex_cache, rays_cfg):
        image = torch_radon_cuda.backward(x, angles, tex_cache, rays_cfg)
        ctx.tex_cache = tex_cache
        ctx.rays_cfg = rays_cfg
        ctx.save_for_backward(angles)

        return image

    @staticmethod
    def backward(ctx, grad_x):
        if not grad_x.is_contiguous():
            grad_x = grad_x.contiguous()

        angles, = ctx.saved_variables
        grad = torch_radon_cuda.forward(grad_x, angles, ctx.tex_cache, ctx.rays_cfg)
        return grad, None, None, None
