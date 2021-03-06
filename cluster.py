#階層的クラスタリング

def readfile(filename):
    file = open(filename)
    lines = []
    for line in file:
      lines.append(line)
    #lines=[line for line in file(filename)]
    file.close()
    # 最初の行は列のタイトル
    colnames=lines[0].strip().split(' ')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        print(p)
        # それぞれの行の最初の列は行の名前
        rownames.append(p[0])
        # 行の残りの部分がその行のデータ
        data.append([float(x) for x in p[1:]])
    #print(data)
    return rownames,colnames,data

from math import sqrt

def pearson(v1,v2):
    # 単純な合計
    sum1=sum(v1)
    sum2=sum(v2)

    # 平方の合計
    sum1Sq=sum([pow(v,2) for v in v1])
    sum2Sq=sum([pow(v,2) for v in v2])

    # 積の合計
    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])

    # ピアソンによるスコアの算出
    num=pSum-(sum1*sum2/len(v1))
    den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0: return 0

    return 1.0-num/den

class bicluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
        self.left=left
        self.right=right
        self.vec=vec
        self.id=id
        self.distance=distance

def hcluster(rows,distance=pearson):
    distances={}

    currentclustid=-1
    # クラスタは最初は行たち
    clust=[bicluster(rows[i],id=i) for i in range(len(rows))]

    while len(clust)>1:
        lowestpair=(0,1)
        closest=distance(clust[0].vec,clust[1].vec)

        # すべての組をループし、もっとも距離の近い組を探す
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                # 距離をキャッシュしてあればそれを使う
                if (clust[i].id,clust[j].id) not in distances:
                    distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)

                d=distances[(clust[i].id,clust[j].id)]

                if d<closest:
                    closest=d
                    lowestpair=(i,j)
        # 二つのクラスタの平均を計算する
        mergevec=[(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))]

        # 新たなクラスタを作る
        newcluster=bicluster(mergevec,left=clust[lowestpair[0]], right=clust[lowestpair[1]], distance=closest,id=currentclustid)
        # 元のセットではないクラスタのIDは負にする
        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]


def printclust(clust,labels=None,n=0):
    # 階層型のレイアウトにするためにインデントする
    for i in range(n):
       print(' ', end="")
    if clust.id<0:
        # 負のidは、枝を示す
        print('--', end="")
    else:
        # 正のidは、終端を示す
        if labels==None:
           print(clust.id)
        else:
           print(labels[clust.id])

    # 右と左の枝を表示する
    if clust.left!=None:
       printclust(clust.left,labels=labels,n=n+1)
    if clust.right!=None:
       printclust(clust.right,labels=labels,n=n+1)
     
#K-平均法によるクラスタリング
    
import random
def kcluster(rows,distance=pearson,k=4):
    # それぞれのポイントの最小値と最大値を決める
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))]

    # 重心をランダムにk個配置する
    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

    lastmatches=None
    for t in range(100):
        print ('Iteration %d' % t)
        bestmatches=[[] for i in range(k)]

        # それぞれの行に対して、もっとも近い重心を探し出す
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0
            for i in range(k):
                d=distance(clusters[i],row)
                if d<distance(clusters[bestmatch],row): bestmatch=i
            bestmatches[bestmatch].append(j)

        # 結果が前回と同じであれば完了
        if bestmatches==lastmatches: break
        lastmatches=bestmatches

        # 重心をそのメンバーの平均に移動する
        for i in range(k):
            avgs=[0.0]*len(rows[0])
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
                clusters[i]=avgs

    return bestmatches


#多次元尺度構成法(MDS)

def scaledown(data,distance=pearson,rate=0.01):
    n=len(data)

    # アイテムの全ての組の実際の距離
    realdist=[[distance(data[i],data[j]) for j in range(n)] for i in range(0,n)]

    # 2次元上にランダムに配置するように初期化
    loc=[[random.random(),random.random()] for i in range(n)]
    fakedist=[[0.0 for j in range(n)] for i in range(n)]

    lasterror=None
    for m in range(0,1000):
        # 予測距離を測る
        for i in range(n):
            for j in range(n):
                fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))

        # ポイントの移動
        grad=[[0.0,0.0] for i in range(n)]
        totalerror=0
        for k in range(n):
            for j in range(n):
                if j==k: continue
                # 誤差は距離の差の百分率
                errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]

                # 他のポイントへの誤差に比例して、各ポイントを
                # 近づけたり遠ざけたりする必要がある
                grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
                grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm

            # 誤差の合計を記録
            totalerror+=abs(errorterm)
        print (totalerror)

        # ポイントを移動することで誤差が悪化したら終了
        if lasterror and lasterror<totalerror: break
        lasterror=totalerror

        # 学習率と傾斜を掛け合わせてそれぞれのポイントを移動
        for k in range(n):
            loc[k][0]-=rate*grad[k][0]
            loc[k][1]-=rate*grad[k][1]

    return loc

if __name__ == '__main__':
  yamanote,words,data=readfile('yamanote_E.txt')
  #yamanote,words,data=readfile('blogdata.txt')
  #print("----")
  #print(yamanote)
  #print(words)
  #print(data)
  #print("----")
  
  clust=hcluster(data)
  printclust(clust,words)
  #print(clust.id)
  #print(clust.left.id)
  #kclust=kcluster(data, k=10)
  #[yamanote[r] for r in kclust[0]]
  #[yamanote[r] for r in kclust[1]]
  
  #coords=scaledown(data)
  #print(coords)
