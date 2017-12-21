from math import sqrt

critics={
   'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
   'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
   'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0},
   'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0,
'You, Me and Dupree': 2.5},
   'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0},
   'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
   'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0},
   'Taro':{'Lady in the Water': 4.0,'Snakes on a Plane': 3.5,'Just My Luck': 2.5, 'Superman Returns': 4.0}
}

# person1とperson2の距離を基にした類似性スコアを返す
def sim_distance(prefs,person1,person2):
# 二人とも評価しているアイテムのリストを得る 
   si={}
   for item in prefs[person1]:
      if item in prefs[person2]: 
         si[item]=1
# 両者共に評価しているものが1つもなければ0を返す 
   if len(si)==0: 
      return 0
# すべての差の平方を足し合わせる 
   sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
      for item in prefs[person1] if item in prefs[person2]]) 
   return 1/(1+sum_of_squares)

def sim_pearson(prefs,p1,p2):
# 両者が互いに評価しているアイテムのリストを取得 
   si={}
   for item in prefs[p1]:
      if item in prefs[p2]: si[item]=1
   
   # 要素の数を調べる 
   n=len(si)
   
   # ともに評価しているアイテムがなければ0を返す
   if len(si)==0: return 0


   # 全ての嗜好を合計する 
   sum1=sum([prefs[p1][it] for it in si]) 
   sum2=sum([prefs[p2][it] for it in si])
   # 平方を合計する 
   sum1Sq=sum([pow(prefs[p1][it],2) for it in si]) 
   sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
   # 積を合計する 
   pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
   # ピアソンによるスコアを計算する
   num=pSum-(sum1*sum2/n)
   den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n)) 
   if den==0: return 0
   r=num/den
   return r



# ディクショナリprefsからpersonにもっともマッチするものたちを返す # 結果の数と類似性関数はオプションのパラメータ
def topMatches(prefs,person,n=5,similarity=sim_pearson):
   scores=[(similarity(prefs,person,other),other) for other in prefs if other!=person]
   #高スコアがリストの最初に来るように並び替える 
   scores.sort()
   scores.reverse()
   return scores[0:n]


# person以外の全ユーザの評点の重み付平均を使い、personへの推薦を算出する
def getRecommendations(prefs,person,similarity=sim_pearson):
   totals={}
   simSums={}
   for other in prefs:
      # 自分自身とは比較しない
      if other==person: continue 
      sim=similarity(prefs,person,other)
      # 0以下のスコアは無視
      if sim<=0: continue
      for item in prefs[other]:
         # まだ見ていない映画の得点のみを算出
         if item not in prefs[person] or prefs[person][item]==0:
         # 類似度 * スコア 
            totals.setdefault(item,0)
            totals[item]+=prefs[other][item]*sim
            # Sum of similarities
            simSums.setdefault(item,0)
            simSums[item]+=sim
   # 正規化したリストを作る
   rankings=[(total/simSums[item],item) for item,total in totals.items()]
   # ソートしたリストを返す
   rankings.sort()
   rankings.reverse()
   return rankings


#ディクショナリのキーと値を変換する
def transformPrefs(prefs):
   result={}
   for person in prefs:
      for item in prefs[person]:
         result.setdefault(item,{})
         # itemとpersonを入れ替える
         result[item][person]=prefs[person][item] 
   return result


def calculateSimilarItems(prefs,n=10):
   # アイテムをキーとして持ち、それぞれのアイテムに似ている #アイテムのリストを値として持つディクショナリを作る。
   result={}
   # 嗜好の行列をアイテム中心な形に反転させる
   itemPrefs=transformPrefs(prefs)
   c=0
   for item in itemPrefs:
   # 巨大なデータセット用にステータスを表示
      c+=1
      if c%100==0:  print("{}/{}".format(c,len(itemPrefs)))
      # このアイテムにもっとも似ているアイテムたちを探す 
      scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
      result[item]=scores
   return result

def getRecommendedItems(prefs,itemMatch,user): 
   userRatings=prefs[user]
   scores={}
   totalSim={}
   # このユーザに評価されたアイテムをループする
   for (item,rating) in userRatings.items( ):
      # このアイテムに似ているアイテムたちをループする
      for (similarity,item2) in itemMatch[item]:
         # このアイテムに対してユーザがすでに評価を行っていれば無視する
         if item2 in userRatings: continue
         # 評点と類似度を掛け合わせたものの合計で重みづけする
         scores.setdefault(item2,0)
         scores[item2]+=similarity*rating
         # すべての類似度の合計
         totalSim.setdefault(item2,0)
         totalSim[item2]+=similarity

   # 正規化のため、それぞれの重みづけしたスコアを類似度の合計で割る
   rankings=[(score/totalSim[item],item) for item,score in scores.items( )]
   # 降順に並べたランキングを返す
   rankings.sort( )
   rankings.reverse( )
   return rankings


if __name__ == '__main__':
   print(critics['Taro']['Lady in the Water'])
   matches = topMatches(critics, 'Taro', n=3)
   print("near by Taro")
   for i in range(len(matches)):
      print(matches[i])
   recomUserMatches = getRecommendations(critics, 'Taro')
   print("recommend Taro")
   for i in range(len(recomUserMatches)):
      print(recomUserMatches[i])
   itemsim=calculateSimilarItems(critics)
   recomItemMatches = getRecommendedItems(critics,itemsim,'Toby')
   print("recommend Taro")
   for i in range(len(recomItemMatches)):
      print(recomItemMatches[i])
