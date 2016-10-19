LD_LIBRARY_PATH=toxwrapper/build \
GI_TYPELIB_PATH=toxwrapper/build \
G_MESSAGES_DEBUG=all \
GOBJECT_DEBUG=instance-count \
bundle exec ruby -d bcdice.rb
