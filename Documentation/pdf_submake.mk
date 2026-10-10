# -*- makefile -*-
# To be included into Documentation/Makefile when $(PDF_SUBMAKE) != 0

# In case $(PDF_SUBMAKE) is not set ...
ifneq ($(PDF_SUBMAKE),0)

htmldocs mandocs infodocs texinfodocs latexdocs epubdocs xmldocs linkcheckdocs:
	$(Q)PYTHONPYCACHEPREFIX="$(PYTHONPYCACHEPREFIX)" \
		$(srctree)/tools/docs/sphinx-pre-install --version-check
	+$(Q)PYTHONPYCACHEPREFIX="$(PYTHONPYCACHEPREFIX)" \
		$(PYTHON3) $(BUILD_WRAPPER) $@ \
		--sphinxdirs="$(SPHINXDIRS)" $(RUSTDOC) \
		--builddir="$(BUILDDIR)" \
		--theme=$(DOCS_THEME) --css=$(DOCS_CSS) --paper=$(PAPER)
# Special handling for pdfdocs
# User-friendly check for pdflatex and latexmk
HAVE_PDFLATEX := $(shell if which $(PDFLATEX) >/dev/null 2>&1; then echo 1; else echo 0; fi)
HAVE_LATEXMK := $(shell if which latexmk >/dev/null 2>&1; then echo 1; else echo 0; fi)

ifeq ($(HAVE_PDFLATEX),0)
pdfdocs:
	$(warning The '$(PDFLATEX)' command was not found. Make sure you have it installed and in PATH to produce PDF output.)
	@echo "  SKIP    Sphinx $@ target."
else #HAVE_PDFLATEX
ifeq ($(HAVE_LATEXMK),1)
pdfdocs: PDFLATEX := latexmk -$(PDFLATEX)
endif #HAVE_LATEXMK
pdfdocs: DENY_VF = XDG_CONFIG_HOME=$(FONTS_CONF_DENY_VF)
pdfdocs: latexdocs
ifeq ($(SPHINXDIRS),.)
	$(Q)$(MAKE) PDFLATEX="$(PDFLATEX)" LATEXOPTS="$(LATEXOPTS)" $(DENY_VF) -C $(BUILDDIR)/latex || \
	  PYTHONPYCACHEPREFIX="$(PYTHONPYCACHEPREFIX)" $(srctree)/tools/docs/check-variable-fonts.py
	$(Q)mkdir -p $(BUILDDIR)/pdf
	$(Q)ln -srf $(subst .tex,.pdf,$(abspath $(wildcard $(BUILDDIR)/latex/*.tex))) -t $(BUILDDIR)/pdf/
	@echo "Symlinks to PDFs are under $(abspath $(BUILDDIR))/pdf/."
else #SPHINXDIRS
	$(Q)$(MAKE) Q="$(Q)" BUILDDIR="$(BUILDDIR)" SPHINXDIRS="$(SPHINXDIRS)" -f $(srctree)/Documentation/pdf_makefile afterlatex
	$(Q)$(MAKE) Q="$(Q)" BUILDDIR="$(BUILDDIR)" SPHINXDIRS="$(SPHINXDIRS)" PDFLATEX="$(PDFLATEX)" LATEXOPTS="$(LATEXOPTS)" DENY_VF="$(DENY_VF)" srctree="$(srctree)" -f $(srctree)/Documentation/pdf_makefile || \
	  PYTHONPYCACHEPREFIX="$(PYTHONPYCACHEPREFIX)" $(srctree)/tools/docs/check-variable-fonts.py
	$(Q)$(MAKE) Q="$(Q)" BUILDDIR="$(BUILDDIR)" SPHINXDIRS="$(SPHINXDIRS)" srctree="$(srctree)" -f $(srctree)/Documentation/pdf_makefile symlink-pdf
endif #SPHINXDIRS
	$(Q)$(MAKE) BUILDDIR="$(BUILDDIR)" SPHINXDIRS="$(SPHINXDIRS)" -f $(srctree)/Documentation/pdf_makefile check-pdf
endif #HAVE_PDFLATEX
endif #PDF_SUBMAKE
