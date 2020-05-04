# ラズパイ構築メモ
ラズパイ(多分3)構築のメモ。  
目標としては、
* 録画サーバー構築
* ファイルサーバー構築
  
ができるようにすること。

## 参考文献
>Raspberry Pi 4 と NAS で録画環境を整える(kumak1’s blog)  
>https://kumak1.hatenablog.com/entry/2020/01/02/202308  
> 8回目 録画サーバー立った！Mirakrun＋Chinashu
> https://study.engineergirl.work/?p=184  
> Raspberry Pi 3 ModelB で外付けHDDをファイルサーバー化する  
> https://qiita.com/marumen/items/de150089d95f52849e5b  

## 初期設定
* 2019-04-08-raspbian-stretchを書き込み
* E:boot内に"ssh"というファイルを作成(拡張子不要)
* E:boot内に"wpa_supplicant.conf"というファイルを作成して下記を記載する。
  
  ```
  country=JP
  update_config=1
  ctrl_interface=/var/run/wpa_supplicant

  network={
    scan_ssid=1
    ssid="ssid名"
    psk="パスワード"
  }
  ```

* ラズパイ起動(起動完了に1分ほどかかるらしい)。
* sshで接続する
  
  ```Bash:ssh
  ssh -l pi IPアドレス
  初期パスワード：raspberry
  ```

<strike>
* sudo raspi-configで設定画面を開き、
  * 1 Change User Passwordで初期パスワードを変更する。
  * 3 BootOptions > B2 Wait for Network at Boot で起動時にネットワーク関連処理を待つのを有効化する。この設定をしておかないと、後述のfstab設定をしたとしても起動時にNASを自動マウントしなくなる。
* /etc/dhcpcd.confに下記を追加してIPアドレスを固定する。なお、下記はサンプルであり、実際は固定したいIPアドレスに変更すること。
  
  ```
  interface wlan0
  static ip_address=192.168.10.128/24
  static routers=192.168.10.1
  stacit domain_name_servers=192.168.10.1 8.8.8.8
  ```

* ssh公開鍵を設定する
  * ラズパイで下記を実行
  
    ```
    pi@raspberrypi:~ $ mkdir .ssh
    pi@raspberrypi:~ $ touch .ssh/authorized_keys
    pi@raspberrypi:~ $ chmod 700 .ssh
    pi@raspberrypi:~ $ chmod 600 .ssh/authorized_keys
    ```
  * windwosで下記を実行して公開鍵を転送する
    
    ```
    scp C:\Users\Naoto\.ssh\id_rsa.pub pi@192.168.137.222:~/.ssh/authorized_keys
    ```
</strike>

## システム時刻を合わせる
* 現在時刻を表示するコマンド
  ```
  date
  ```
* 時刻を日本に合わせる
  ```
  sudo timedatectl set-timezone Asia/Tokyo
  ```
* 起動時にシステム時刻を変更する
  ```
  cd /etc/init.d/
  sudo vi autorun_date
  ```
  ```
  #!/bin/sh
  ### BEGIN INIT INFO
  # Provides: mathkernel
  # Required-Start: $local_fs
  # Required-Stop: $local_fs
  # Default-Start: 2 3 4 5
  # Default-Stop: 0 1 6
  # Short-Description: mathkernel
  ### END INIT INFO

  #システム時刻を日本に合わせる
  sudo timedatectl set-timezone Asia/Tokyo
  ```
* スクリプトに実行権限を与える
  ```
  sudo chmod 755 autorun_date
  ```
* スクリプトが自動実行するようにシステムに登録する
  ```
  sudo update-rc.d autorun_date defaults
  ```
* 再起動
  ```
  sudo reboot
  ```

## 録画サーバーを構築する for 2020/5/4
* aptリポジトリ一覧を更新
  ```
  sudo apt update
  ```
* ビルドに必要なものやカードリーダーラーブラリを導入
  ```
  pi@raspberrypi:~ $ sudo curl -sL https://deb.nodesource.com/setup_12.x | sudo bash -
  pi@raspberrypi:~ $ sudo apt-get install -y vim cmake autoconf nodejs pcscd pcsc-tools libpcsclite-dev libccid vainfo
  ```
* 動作確認
  ```
  sudo pcsc_scan
  ```
* TVチューナーのファームウェアを導入する。

    ```
    pi@raspberrypi:~ $ cd Downloads/
    pi@raspberrypi:~/Downloads $ wget http://plex-net.co.jp/plex/px-s1ud/PX-S1UD_driver_Ver.1.0.1.zip
    pi@raspberrypi:~/Downloads $ unzip PX-S1UD_driver_Ver.1.0.1.zip
    pi@raspberrypi:~/Downloads $ sudo cp PX-S1UD_driver_Ver.1.0.1/x64/amd64/isdbt_rio.inp /lib/firmware/
    ```
* B-CASのでコードライブラリを導入
  
    ```
    pi@raspberrypi:~/Downloads $ wget https://github.com/stz2012/libarib25/archive/master.zip
    pi@raspberrypi:~/Downloads $ unzip master.zip
    pi@raspberrypi:~/Downloads $ cd ibarib25-master
    pi@raspberrypi:~/Downloads/libarib25-master $ cmake .
    pi@raspberrypi:~/Downloads/libarib25-master $ make
    pi@raspberrypi:~/Downloads/libarib25-master $ sudo make install
    pi@raspberrypi:~/Downloads/libarib25-master $ cd ..
    ```
* 録画用コマンドの導入
    ```
    pi@raspberrypi:~/Downloads $ wget http://www13.plala.or.jp/sat/recdvb/recdvb-1.3.2.tgz
    pi@raspberrypi:~/Downloads $ tar xvzf recdvb-1.3.2.tgz
    pi@raspberrypi:~/Downloads $ cd recdvb-1.3.2/
    pi@raspberrypi:~/Downloads/recdvb-1.3.2 $ ./autogen.sh
    pi@raspberrypi:~/Downloads/recdvb-1.3.2 $ ./configure --enable-b25
    pi@raspberrypi:~/Downloads/recdvb-1.3.2 $ make
    pi@raspberrypi:~/Downloads/recdvb-1.3.2 $ sudo make install
    ```
* Mirakurun(チューナーサーバー)の導入
  ```
  pi@raspberrypi:~/Downloads $ sudo npm install pm2 -g
  pi@raspberrypi:~/Downloads $ sudo npm install mirakurun -g --unsafe-perm --production
  pi@raspberrypi:~/Downloads $ sudo mirakurun init
  ```
* Mirakurunにチューナーの設定を追記
  ```
  pi@raspberrypi:~/Downloads $ sudo mirakurun config tuners
  ```
  ```
  - name: PX-S1UD-1
    types:
      - GR
    command: recdvb --b25 --dev 0 <channel> - -
  ```
  ```
  pi@raspberrypi:~/Downloads $ sudo mirakurun restart
  pi@raspberrypi:~/Downloads $ curl -X PUT "http://localhost:40772/api/config/channels/scan"
  pi@raspberrypi:~/Downloads $ sudo mirakurun restart
  ```
  * curl -X PUT "http://localhost:40772/api/config/channels/scan"でcurl(7)エラーが出る
    * ゼロからやり直し。makeとかする時に全部sudoつけたら出来たけど、結局原因不明。
  * curl -X PUT "http://localhost:40772/api/config/channels/scan"でno sigmalしか出ない
    * sudo rebootで再起動後やり直す
* Mirakurun 経由で、TVチューナー・B-CASのデコード・録画用コマンドが動作するか確認
  ```
  # VLC でネットワークストリーム再生
  http://192.168.10.128:40772/api/channels/GR/25/stream
  ```
* Chinachu(録画サーバー)の導入
  ```
  pi@raspberrypi:~/Downloads $ git clone https://github.com/Chinachu/Chinachu.git
  pi@raspberrypi:~/Downloads $ cd Chinachu/
  pi@raspberrypi:~/Downloads/Chinachu $ ./chinachu installer

  # 1) Auto (full) を選択
  ```
* ARM（Raspberry Pi）だと Chinachu は node と ffmpeg をうまく扱えないので、手動でシンボリックリンクを貼る。
  ```
  pi@raspberrypi:~/Downloads/Chinachu $ cd .nave
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ rm node
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ rm npm
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ ln -s /usr/bin/node .
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ ln -s /usr/bin/npm .
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ cd ../usr/bin
  pi@raspberrypi:~/Downloads/Chinachu/usr/bin $ rm avconv
  pi@raspberrypi:~/Downloads/Chinachu/usr/bin $ rm avprobe
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ ln -s /usr/bin/ffmpeg avconv
  pi@raspberrypi:~/Downloads/Chinachu/.nave $ ln -s /usr/bin/ffprobe avprobe
  ```
  ```
  pi@raspberrypi:~/Downloads/Chinachu $ echo [] > rules.json
  pi@raspberrypi:~/Downloads/Chinachu $ cp config.sample.json config.json
  pi@raspberrypi:~/Downloads/Chinachu $ vim config.json
  # `"uid": "pi",` `"recorderdDir": "/mnt/nas/recorded/"` へ変更
    ```
  * Chinachu の起動と自動起動。前後に sudo reboot して再起動しておくと良い。
  ```
  pi@raspberrypi:~/Downloads/Chinachu $ sudo reboot
  pi@raspberrypi:~/Downloads/Chinachu $ sudo pm2 start processes.json
  pi@raspberrypi:~/Downloads/Chinachu $ sudo pm2 save
  pi@raspberrypi:~/Downloads/Chinachu $ sudo reboot
  ```
  <strike>
* chinachuを起動
  ```
  pi@raspberrypi: $ cd /Downloads/Chinachu
  pi@raspberrypi:~/Downloads/Chinachu $ sudo pm2 start processes.json
  ```
  </strike>

* 本当ならこれでブラウザアクセスすれば見れるらしいんだけど、なんか見れなかった。  下記コマンドでchinachuを起動する。
  ```
  ./chinachu service wui execute
  # 問題なく起動できたらCtrl+Cで終了

  ./chinachu update
  # EPG取得テスト（エラーが出た場合は恐らく Mirakurun に接続できていません）
  ```
  ```
  ./chinachu service wui execute
  http://[IPアドレス]:20772/
  ```

## Sambaファイルサーバーを構築する for 2020/5/4
* 外付けHDDをマウントする
  ```
  $ sudo fdisk -l
  ...中略
  Device     Boot Start        End    Sectors   Size Id Type
  /dev/sda1        2048 1953520064 1953518017 931.5G  7 HPFS/NTFS/exFAT
  ```
* 再起動時に自動的にマウントされるように設定
  ```
  $ sudo blkid /dev/sda1
  /dev/sda1: LABEL="EC-PHU3" UUID="A6761F43761F13A1" TYPE="ntfs" PARTUUID="7a469053-01"
  ```
* /etc/fstabに以下を追記。
  ```
  UUID="A6761F43761F13A1" /mnt/hdd ntfs-3g defaults,nofail 0       0
  ```

* sambaをインストールする
  ```
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install samba
  ```
* Sambaの設定ファイルに追記する
  ```
  sudo cp /etc/samba/smb.conf /etc/samba/smb.conf_backup
  sudo vi /etc/samba/smb.conf
  ```
  ```
  [share]
  comment = Share
  path = /mnt/hdd
  public = yes
  read only = no
  browsable = yes
  force user = pi
  ```
* confファイルのチェック
  ```
  testparm

  Loaded services file OK.と出ればOK
  ```
* Sambaサービスの再起動
  ```
  sudo systemctl restart smbd
  ```