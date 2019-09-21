# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class CcclConan(ConanFile):
    name = "cccl_installer"
    version = "1.1"
    license = "GPL-3.0-or-later"
    url = "https://www.github.com/bincrafters/conan-cccl"
    homepage = "https://github.com/swig/cccl/"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Unix cc compiler to Microsoft's cl compiler wrapper"
    topics = ("conan", "msvc", "Visual Studio", "wrapper", "gcc")
    exports = ["LICENSE.md", ]
    no_copy_source = True
    options = {
        "muffle": [True, False],
        "verbose": [True, False],
    }
    default_options = {
        "muffle": True,
        "verbose": False,
    }
    settings = "compiler",

    _source_subfolder = "source_subfolder"

    def package_id(self):
        del self.info.settings.compiler
        del self.info.options.muffle
        del self.info.options.verbose

    def source(self):
        filename = "cccl-{}.tar.gz".format(self.version)
        url = "https://github.com/swig/cccl/archive/{}".format(filename)
        sha256 = "aeb456d36dc5c824b4db334286f24dbedddd026d600d24f58e62a60a2d2ff901"

        tools.get(url, sha256=sha256)
        os.rename("cccl-cccl-{}".format(self.version), self._source_subfolder)

        cccl_path = os.path.join(self.source_folder, self._source_subfolder, "cccl")
        tools.replace_in_file(cccl_path,
                              "    --help)",
                              "    *.lib)\n"
                              "        linkopt+=(\"$lib\")"
                              "        ;;\n\n"
                              "    --help)")
        tools.replace_in_file(cccl_path,
                              "clopt+=(\"$lib\")",
                              "linkopt+=(\"$lib\")")
        tools.replace_in_file(cccl_path,
                              "    -L*)",
                              "    -LIBPATH:*)\n"
                              "        linkopt+=(\"$1\")\n"
                              "        ;;\n\n"
                              "    -L*)")

    def package(self):
        self.copy("cccl", src=os.path.join(self.source_folder, self._source_subfolder), dst="bin")
        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        if self.settings.compiler != "Visual Studio":
            self.output.warn("Adding cccl compiler wrapper for non-Visual Studio compiler."
                             " Verify whether this is correct!")

        self.cpp_info.bindirs = ["bin", ]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        cccl_args = [
            "sh",
            os.path.join(self.package_folder, "bin", "cccl"),
        ]
        if self.options.muffle:
            cccl_args.append("--cccl-muffle")
        if self.options.verbose:
            cccl_args.append("--cccl-verbose")
        cccl = " ".join(cccl_args)

        self.output.info("Setting CC to '{}'".format(cccl))
        self.env_info.CC = cccl
        self.output.info("Setting CXX to '{}'".format(cccl))
        self.env_info.CXX = cccl
        self.output.info("Setting LD to '{}'".format(cccl))
        self.env_info.LD = cccl
