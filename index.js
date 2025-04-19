require('dotenv').config();
const { Client, GatewayIntentBits, Partials, EmbedBuilder } = require('discord.js');
const { joinVoiceChannel } = require('@discordjs/voice');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildVoiceStates,
  ],
  partials: [Partials.Channel],
});

client.once('ready', () => {
  console.log(`✅ Bot is ready as ${client.user.tag}`);
});

client.on('messageCreate', async message => {
  if (!message.content.startsWith('r!') || message.author.bot) return;

  const args = message.content.slice(2).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  // r!icon
  if (command === 'icon') {
    const icon = message.guild.iconURL({ dynamic: true, size: 1024 });
    const embed = new EmbedBuilder()
      .setTitle(`Ikon Server - ${message.guild.name}`)
      .setImage(icon)
      .setColor('Blue');
    message.reply({ embeds: [embed] });
  }

  // r!link
  else if (command === 'link') {
    try {
      const invite = await message.channel.createInvite({ maxAge: 0, maxUses: 0 });
      message.reply(`🔗 Invite link: ${invite.url}`);
    } catch {
      message.reply('❌ Tidak dapat membuat invite link di channel ini.');
    }
  }

  // r!avatar
  else if (command === 'avatar') {
    const user = message.mentions.users.first() || message.author;
    const embed = new EmbedBuilder()
      .setTitle(`${user.username}'s Avatar`)
      .setImage(user.displayAvatarURL({ dynamic: true, size: 1024 }))
      .setDescription(`**Username:** ${user.tag}\n**User ID:** ${user.id}`)
      .setColor('Random');
    message.reply({ embeds: [embed] });
  }

  // r!join <nama channel>
  else if (command === 'join') {
    const channelName = args.join(' ');
    if (!channelName) return message.reply('❌ Masukkan nama voice channel, contoh: `r!join Rissyrissy`');

    const voiceChannel = message.guild.channels.cache.find(
      c => c.type === 2 && c.name.toLowerCase() === channelName.toLowerCase()
    );

    if (!voiceChannel) return message.reply(`❌ Voice channel "${channelName}" tidak ditemukan.`);

    try {
      joinVoiceChannel({
        channelId: voiceChannel.id,
        guildId: voiceChannel.guild.id,
        adapterCreator: voiceChannel.guild.voiceAdapterCreator,
      });

      message.reply(`🎧 Bot telah join ke voice channel: **${voiceChannel.name}**`);
    } catch (err) {
      console.error(err);
      message.reply('❌ Gagal join ke voice channel.');
    }
  }
});

client.login(process.env.DISCORD_TOKEN);
