# othello
オセロです.

othello.pyを動かせばオセロが出来ます。

UI等はまだ作っていないため，標準入力でプレイします。

また、エラー用出力等がまだ残っています

numpy

tesorflow

keras
．
<details>
<summary>雑記</summary>
<pre>
<code>
概要：
alphazeroの仕組みを用いたオセロプログラムは本プログラム以外にも多数存在している．
alphazeroは一般的な二人零和有限確定完全情報ゲームの全てに適応できる高い汎用性が評価されている．
しかし，オセロプログラムを考えた場合，使える情報は増える．
よって、終盤ソルバーとalphazeroを組み合わせたプログラムを作ろうというのが本プログラムである．
終盤ソルバーと組み合わせる利点は三つほどある
1、そもそも終盤ソルバーによるものは必ず最適解なため，終盤に強くなる
  →純粋に強くなる
2、終盤を学習に入れないため，序中盤に特化したネットワークになることが期待される
  →オセロは序中盤は着手可能手が多い方が良いが最終的な評価は石の数になるため，切り分けが効果的だったりする
3、完璧な学習データを複製できる
  →ソルバーで出た答えは最適解であるため，policyネットやvalueネットに最適解を入れることが出来る
これらの理由から終盤ソルバーを利用したalphazeroを作成してみた．

仕様：
100回ゲームを行い学習用データを用意する．ソルバーは最後の12手前から行い，学習用データとして，上位四分の一程度の手(2～４手)を複製して保存する．
また，回転での複製も行う．結果として100回のゲームは大体2400回のゲーム数程度に出来る．なお，MCTSの回数は200回，最初の6手はランダムとしている．
ネットワークはresnetで，ブロック数8，フィルタ数64で作成している．
基本的には8×8全ての情報を使った畳み込みを行う場合は3＊3カーネルが8つあれば足りる(ブロック当たり二つなので16個ある)．resnetはスキップコネクトがあるため深くした方が良いには良い
トレーニングにはオプティマイザーをadam，レートを1e-5で計算する．

結果と展望：
結果は現時点ではかなり弱い．
弱い原因は
・自分の環境では学習がほとんど出来ていない．
・高速化が図れず，読みが浅すぎる．
である．
C等で最適化を行えばソルバーはあと200倍程度，モンテカルロツリーの計算は20倍程度速くできると思われる．
また，高速化を図る面で、alphazeroと同じresnetではなく，efficientnetを使うことを考えている．
今のところはこんなところである．

9/28追記
cythonでの最適化により，ソルバーは100倍程度高速化し、16手前読みでも数秒で終わるようになった．(C++でbitの並列処理が出来ればもっと速くなると思われる)
モンテカルロツリーはゲームのコア部分のみcython化したが、1.2倍程度の高速化にしかなっていない．
efficientnetを使用してみた結果はlossや実際に打ってみた結果からも良くなく，速度もresnet並みだったため取りやめた。
学習量を増やせば改善される気もするが，計算資源が乏しいため諦める．
加えて、計算のボトルネックはネットワークの順伝播ではなくモンテカルロツリーの計算だったため、resnetをより大きくした(ブロック数16,フィルタ数128)
</code>
</pre>
</details>
