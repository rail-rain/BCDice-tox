require 'gir_ffi'
$LOAD_PATH << "#{File.dirname(__FILE__)}/BCDice/src/"
require 'bcdiceCore'

GirFFI.setup :ToxWrapper

module GirFFI
  class SizedArray
    def length
      @size
    end
  end
end

ToxWrapper.load_class :Friend
ToxWrapper.load_class :Group
module ToxWrapper
  class Friend
    def to_s
      self.name
    end
  end

  class Group
    def to_str
      self.to_s
    end
  end
end

class BCDice
  def cutMessageCommend(message)
    case message
    when /(^|\s+)(#{$OPEN_DICE}|#{$OPEN_PLOT})(\s+|$)/i
      return message
    when /^set\s.+/i
      return message
    end
    index = message.index(/\s/)
    unless( index.nil? )
      message = message[0...index]
    end

    return message
  end
end

SAVE_FILE = 'BCDice.tox'

class Bot

  def initialize
    diceMaker = BCDiceMaker.new
    @dice = diceMaker.newBcDice
    @dice.setIrcClient(self)
    @friends = []

    options = ToxWrapper::Options::create
    is_new = !File.exist?(SAVE_FILE)
    @tox = ToxWrapper::Tox.new(options, SAVE_FILE, nil, is_new)

    @tox.username = $nick
    @tox.status_message = $userName

    GObject.signal_connect(@tox, "notify::connected") {puts "bot id: #{@tox.id}"}

    GObject.signal_connect(@tox, "friend_request") do |tox, id|
      friend = tox.accept_friend_request(id)
      GObject.signal_connect(friend, "message") {|f, m| friend_message(f, m)}
      @friends << friend
    end
    GObject.signal_connect(@tox, "friend_online") do |_, friend|
      GObject.signal_connect(friend, "message") {|f, m| friend_message(f, m)}
      @friends << friend
    end
    GObject.signal_connect(@tox, "group_invite") do |tox, friend, type, group_pubkey|
      group = tox.join_groupchat(friend, type, group_pubkey)
      GObject.signal_connect(group, "message") {|g, n, m| group_message(g, n, m)}
    end
  end

  def friend_message(friend, message)
    tnick = "";
    if( /->/ =~ message )
      message, tnick, *dummy = message.split(/->/)
    end
    @dice.setMessage(message)
    @dice.recieveMessage(friend, tnick)
  end

  def group_message(group, peer_number, message)
    @dice.setMessage(message)
    @dice.setChannel(group)
    @dice.recievePublicMessage(@dice.getGameType)
  end

  def run
    @tox.run_loop
    @mainloop = GLib::MainLoop.new(nil, false)
    @mainloop.run
  end

  def quit
    @friends.each {|f| f.send_message($quitMessage)}
    GLib.timeout_add(GLib::PRIORITY_DEFAULT, 5) {
      @tox.save_data
      @tox.disconnect
      @mainloop.quit
    }
  end

  def sendMessage(group, message)
    GLib.timeout_add(GLib::PRIORITY_DEFAULT, 10) {
      group.send_message(message)
    }
  end

  def sendMessageToOnlySender(friend, message)
    friend.send_message(message)
  end

  def sendMessageToChannels(message)
    @friends.each {|f| f.send_message(message)}
  end
end

bot = Bot.new
bot.run
