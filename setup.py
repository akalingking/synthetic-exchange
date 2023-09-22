import os
import sys
import subprocess
import datetime
import numpy as np
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize

is_posix = os.name == "posix"
project_name = "synthetic-exchange"
project_dir = project_name.replace("-", "_")

if is_posix:
    os_name = subprocess.check_output("uname").decode("utf8")
    if "Darwin" in os_name:
        os.environ["CFLAGS"] = "-stdlib=libc++ -std=c++11"
    else:
        os.environ["CFLAGS"] = "-std=c++11"

if os.environ.get("WITHOUT_CYTHON_OPTIMIZATIONS"):
    os.environ["CFLAGS"] += " -O0"


def get_version():
    version = datetime.datetime.now().strftime("%Y%m%d")
    try:
        fname = f"./{project_dir}/VERSION"
        with open(fname, "r") as f:
            version = f.read().strip()
    except IOError:
        print(f"error reading file: {fname}")
    return version


def get_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return ""


def get_requirements():
    try:
        with open("requirements.txt") as f:
            return f.read().splitlines()
    except IOError:
        return []


# Avoid a gcc warning below:
# cc1plus: warning: command line option ???-Wstrict-prototypes??? is valid
# for C/ObjC but not for C++
class BuildExt(build_ext):
    def build_extensions(self):
        if os.name != "nt" and "-Wstrict-prototypes" in self.compiler.compiler_so:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        super().build_extensions()


def main():
    cpu_count = os.cpu_count() or 8
    version = get_version()
    packages = find_packages(include=[project_dir, f"{project_dir}.*"])
    package_data = {
        project_name: [
            f"{project_dir}/**/*.cpp",
            f"{project_dir}/**/*.pyx",
            f"{project_dir}/**/*.pxd",
            "VERSION",
            "README.md",
        ],
    }

    install_requires = get_requirements()

    cython_kwargs = {
        "language": "c++",
        "language_level": 3,
    }

    if os.environ.get("WITHOUT_CYTHON_OPTIMIZATIONS"):
        compiler_directives = {
            "optimize.use_switch": False,
            "optimize.unpack_method_calls": False,
        }
    else:
        compiler_directives = {}

    if is_posix:
        cython_kwargs["nthreads"] = cpu_count

    # if "DEV_MODE" in os.environ:
    #    version += ".dev1"
    #    package_data[""] = [
    #        "*.pxd", "*.pyx", "*.h"
    #    ]
    #    package_data["{project_dir}"].append("strategy/cpp/*.cpp")

    if len(sys.argv) > 1 and sys.argv[1] == "build_ext" and is_posix:
        sys.argv.append(f"--parallel={cpu_count}")

    cython_sources = [f"{project_dir}/**/*.pyx"]
    # Check for test cython files
    if os.path.exists("test"):
        include_test = False
        for f in os.listdir("test"):
            if f.endswith(".pyx"):
                include_test = True
        if include_test:
            cython_sources.append("test/**/*.pyx")

    setup(
        name=project_name,
        version=version,
        description=project_name,
        long_description=get_readme(),
        long_description_content_type="text/markdown",
        url=f"https://github.com/akalingking/{project_name}",
        author="Ariel Kalingking",
        author_email="akalingking@gmail.com",
        license="Private",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        keywords=["trading", "financial market", "high-frequency-trading"],
        packages=packages,
        package_data=package_data,
        install_requires=install_requires,
        ext_modules=cythonize(
            cython_sources,
            compiler_directives=compiler_directives,
            **cython_kwargs,
        ),
        include_dirs=[np.get_include()],
        scripts=[
            # f"bin/{project_name}.py",
        ],
        cmdclass={"build_ext": BuildExt},
    )


if __name__ == "__main__":
    main()
