hicolordir = $(datadir)/icons/hicolor
app_icons = \
	orca-16x16.png	\
	orca-22x22.png	\
	orca-24x24.png	\
	orca-32x32.png	\
	orca-48x48.png	\
	orca-scalable.svg

install-data-local:
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/16x16/apps
	$(INSTALL_DATA) $(srcdir)/orca-16x16.png $(DESTDIR)$(hicolordir)/16x16/apps/orca.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/22x22/apps
	$(INSTALL_DATA) $(srcdir)/orca-22x22.png $(DESTDIR)$(hicolordir)/22x22/apps/orca.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/24x24/apps
	$(INSTALL_DATA) $(srcdir)/orca-24x24.png $(DESTDIR)$(hicolordir)/24x24/apps/orca.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/32x32/apps
	$(INSTALL_DATA) $(srcdir)/orca-32x32.png $(DESTDIR)$(hicolordir)/32x32/apps/orca.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/48x48/apps
	$(INSTALL_DATA) $(srcdir)/orca-48x48.png $(DESTDIR)$(hicolordir)/48x48/apps/orca.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/scalable/apps
	$(INSTALL_DATA) $(srcdir)/orca-scalable.svg $(DESTDIR)$(hicolordir)/scalable/apps/orca.svg

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

uninstall-hook:
	rm -f $(DESTDIR)$(hicolordir)/16x16/apps/orca.png
	rm -f $(DESTDIR)$(hicolordir)/22x22/apps/orca.png
	rm -f $(DESTDIR)$(hicolordir)/24x24/apps/orca.png
	rm -f $(DESTDIR)$(hicolordir)/32x32/apps/orca.png
	rm -f $(DESTDIR)$(hicolordir)/48x48/apps/orca.png
	rm -f $(DESTDIR)$(hicolordir)/scalable/apps/orca.svg
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After uninstall, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

update-icon-cache:

EXTRA_DIST = $(app_icons)
