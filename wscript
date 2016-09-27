#! /usr/bin/env python
# encoding: utf-8

from waflib import Utils

# the following two variables are used by the target "waf dist"
VERSION = '0.1'
APPNAME = 'toxwrapper'

# these variables are mandatory ('/' are converted automatically)
top = '.'
out = 'build'

def options(opt):
	opt.load('compiler_c vala')
	opt.add_option('--enable-docs', action='store_true', default=False, help='Generate user documentation')
	#opt.recurse('tests')

def configure(conf):
	conf.load('compiler_c vala gnu_dirs glib2')
	conf.check_vala(min_version=(0, 28, 0))

	conf.check_cfg(package='glib-2.0', uselib_store='GLIB', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='gio-2.0', uselib_store='GIO', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='gobject-2.0', uselib_store='GOBJECT', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='gmodule-2.0', uselib_store='GMODULE', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='gdk-3.0', uselib_store='GDK', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='gdk-pixbuf-2.0', uselib_store='GDKPIXBUF', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='cairo', uselib_store='CAIRO', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='json-glib-1.0', uselib_store='JSONGLIB', mandatory=1, args='--cflags --libs')
	conf.check_cfg(package='libtoxcore', uselib_store='TOXCORE', mandatory=1, args='--cflags --libs')
	conf.check(lib='toxencryptsave', uselib_store='TOXES', mandatory=1, args='--cflags --libs')
	conf.check(lib='toxav', uselib_store='TOXAV', mandatory=1, args='--cflags --libs')

	# C compiler flags.
	conf.env.append_unique('CFLAGS', [
		'-Wall',
		'-Wno-deprecated-declarations',
		'-Wno-unused-variable',
		'-Wno-unused-but-set-variable',
		'-Wno-unused-function',
		# '-DGETTEXT_PACKAGE="ricin"'
	])
	# Vala compiler flags.
	conf.env.append_unique('VALAFLAGS', [
		'--enable-experimental',
		'--enable-deprecated',
		#'--fatal-warnings'
	])

	#conf.recurse('res tests')

	if conf.options.enable_docs:
		conf.env.ENABLE_DOCS = True
		conf.recurse('docs')

def build(bld):
	bld.load('compiler_c vala')
	#bld.recurse('src')
	#bld.recurse('tests')

	if bld.env.ENABLE_DOCS:
		bld.recurse('docs')

	if bld.cmd == 'install':
		try:
			bld.exec_command(["update-mime-database", Utils.subst_vars("${DATADIR}/mime", bld.env)])
			bld.exec_command(["update-desktop-database", Utils.subst_vars("${DATADIR}/applications", bld.env)])
		except:
			pass

	# Lang files
	# langs = bld(
	# 	features     = 'intltool_po',
	# 	appname      = APPNAME,
	# 	podir        = 'po',
	# 	install_path = "${LOCALEDIR}"
	# )

	# Resources file
	resource = bld(
		features = 'c glib2',
		use      = 'GLIB GIO GOBJECT',
		uselib   = 'cshlib',
		source   = 'res/ricin.gresource.xml',
		target   = 'ricinres'
	)

	# Ricin
	ricin = bld.shlib(
		features         = 'c cshlib glib2',
		use              = 'ricinres',
		packages         = 'glib-2.0 gio-2.0 gobject-2.0 gmodule-2.0 gdk-3.0 gdk-pixbuf-2.0 cairo json-glib-1.0 libtoxcore libtoxencryptsave',
		uselib           = 'GLIB GIO GOBJECT GMODULE GDK GDKPIXBUF CAIRO JSONGLIB TOXCORE TOXAV TOXES',
		vala_target_glib = '2.38',
		source           = bld.path.ant_glob('src/*.vala'),
		vapi_dirs        = 'vapis',
		vala_resources   = 'res/ricin.gresource.xml',
		valaflags        = '--generate-source',
		gir = 'ToxWrapper-' + VERSION ,
		target           = APPNAME,
		header_path      = None,
		install_path     = "${LIBDIR}"
	)

	bld(
		after = APPNAME,
		source = 'ToxWrapper-' + VERSION + '.gir',
		target = 'ToxWrapper-' + VERSION + '.typelib',
		install_path = '${LIBDIR}/girepository-1.0',
		rule = 'g-ir-compiler ${SRC} --shared-library=lib' + APPNAME + '.so --output=${TGT}'
	)
