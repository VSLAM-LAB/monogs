import hashlib
import os.path as osp
import sys

from setuptools import setup, find_packages
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

ROOT = osp.dirname(osp.abspath(__file__))
SIMPLE_KNN = 'submodules/simple-knn'
DIFF_RAST = 'submodules/diff-gaussian-rasterization'


class BuildExt(BuildExtension):
    """torch's BuildExtension with one build directory per environment, so builds for different environments never
    share object files."""

    def finalize_options(self):
        super().finalize_options()
        self.build_temp = osp.join(self.build_temp, hashlib.sha1(sys.prefix.encode()).hexdigest()[:10])


# Package metadata and console scripts live in pyproject.toml. One install covers MonoGS and its two CUDA submodules
# (simple-knn, diff-gaussian-rasterization). GPU targets come from TORCH_CUDA_ARCH_LIST (default: the local GPU).
setup(
    packages=find_packages() + ['simple_knn', 'diff_gaussian_rasterization'],
    package_dir={
        'simple_knn': f'{SIMPLE_KNN}/simple_knn',
        'diff_gaussian_rasterization': f'{DIFF_RAST}/diff_gaussian_rasterization',
    },
    py_modules=['vslamlab_monogs_mono', 'vslamlab_monogs_rgbd'],
    include_package_data=True,
    package_data={
        'gui.gl_render': ['shaders/*.glsl'],
    },
    ext_modules=[
        CUDAExtension(
            name='simple_knn._C',
            sources=[f'{SIMPLE_KNN}/spatial.cu', f'{SIMPLE_KNN}/simple_knn.cu', f'{SIMPLE_KNN}/ext.cpp'],
        ),
        CUDAExtension(
            name='diff_gaussian_rasterization._C',
            sources=[
                f'{DIFF_RAST}/cuda_rasterizer/rasterizer_impl.cu',
                f'{DIFF_RAST}/cuda_rasterizer/forward.cu',
                f'{DIFF_RAST}/cuda_rasterizer/backward.cu',
                f'{DIFF_RAST}/rasterize_points.cu',
                f'{DIFF_RAST}/ext.cpp',
            ],
            extra_compile_args={'nvcc': ['-I' + osp.join(ROOT, DIFF_RAST, 'third_party', 'glm')]},
        ),
    ],
    cmdclass={'build_ext': BuildExt},
)
