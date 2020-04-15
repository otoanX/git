# VisualSutdioCodeでGitHubを使う
## Git及びGitHubとは
Git及びGitHubはファイルのバージョン管理システム。つまり、「書類のどこをどう変えたか」を管理するやつ。  
Gitは自分のパソコンだけでバージョン管理するけど、GitHubはウェブサービスで、世界中に公開することができる。  
会社の皆がGitできるようになると、決裁書とかの修正がめっちゃ早くなるよ。
> 「そもそもGitって何？」、「GitとGitHubは何が違うの？」にシンプルに答えるよ
> https://blog.sixapart.jp/2014-03/mttips-02-what-is-git.html

![](2020-04-05-12-51-36.png)
## 前準備
- Visual Studio Codeをインストールする。
- Visual Studio Codeを日本語化する。  
  1. VisualStudioCodeを開く
  2. viewを選択
  3. command paletteを選択
  4. configure display languageを選択
  5. install additional languageを選択
  6. 左に拡張言語パックが出てくるので、Japanese Language Pack for Visual Studio Codeを探してインストール
  7. VisutalStudioCodeを再起動する
- Gitをインストールする。
  1. https://gitforwindows.org/からダウンロードする
  2. コマンドプロンプトで`git --version`を実行して無事インストールできているか確認する。
  3. GitHub用のユーザ名、メールアドレスの設定を行う
     ```
      git config --global user.name "ユーザ名"
      git config --global user.email "メールアドレス"
     ```
## Git
  Gitの流れは下記となる。  
  1. 変更したファイルを保存する
  2.  変更したファイルをステージング(所謂コミット予定エリア。コマンド：`git add`)する。
  3. ローカルリポジトリにコミットする。
  ![](2020-04-05-13-01-20.png)

## 参考文献
> 君には1時間でGitについて知ってもらう(with VSCode)  
> https://qiita.com/jesus_isao/items/63557eba36819faa4ad9

## 作成メモ
  * "Paste Image"というvscode拡張機能で、マークダウンに「ctrl+Alt+v」で画像を挿入できる。  