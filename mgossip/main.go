/*
 这是一个基于memberlist实现的改进Gossip实验代码。
 这是一个KV键值对分布式系统，系统使用Gossip协议进行各个节点数据的同步
*/

package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/bwmarrin/snowflake"
	"github.com/go-ini/ini"
	"github.com/zhuohuashiyi/mgossip/mgossip"

)

var (
	mtx        sync.RWMutex //  读写锁
	items      = map[string]string{}
	broadcasts *mgossip.TransmitLimitedQueue
	configFile    = flag.String("conf", "config.ini", "配置文件地址")
	nodeName      = flag.String("nodeName", "firstNode", "节点名称")
	gossipNodes   = flag.Int("gossipNodes", 2, "谣言传播节点个数")
	retransmitMult = flag.Int("retransmitMult", 4, "memberlist重传次数因子")
	UDPBufferSize = flag.Int("UDPBufferSize", 1400, "UDP包的最大长度")
	systemBroadcastMult = flag.Int("systemBroadcastMult", 1, "系统广播队列的重传次数因子")
	probeInterval = flag.Int("probeInterval", 5, "probe定时")
	messages = map[int64]int64{}
	bindAddr string
	advertiseAddr string
	bindPort int
	memberlistAddr string
	memberlistPort int
	neighbors []string
	port int
	node *snowflake.Node
)

// init函数负责初始化，主要是配置文件的解析和日志的设置
func init() {   // 初始化函数
	flag.Parse() //  命令行参数解析
	cfg, err := ini.Load(*configFile)
	if err != nil {
		panic("配置文件不存在或者格式有误")
	}
	bindAddr = cfg.Section(*nodeName).Key("bindAddr").String()
	advertiseAddr = cfg.Section(*nodeName).Key("advertiseAddr").String()
	bindPort, err = cfg.Section(*nodeName).Key("bindPort").Int()
	if err != nil {
		fmt.Print(err.Error())
		panic("配置文件解析失败")
	}
	memberlistAddr = cfg.Section(*nodeName).Key("memberlistAddr").String()
	memberlistPort, err = cfg.Section(*nodeName).Key("memberlistPort").Int()
	if err != nil {
		fmt.Print(err.Error())
		panic("配置文件解析失败")
	}
	neighbors = cfg.Section(*nodeName).Key("neighbors").Strings(",")
	port, err = cfg.Section(*nodeName).Key("port").Int()
	if err != nil {
		fmt.Print(err.Error())
		panic("配置文件解析失败")
	}
	logFile, err := os.OpenFile(fmt.Sprintf("logs/%s.log", *nodeName), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println("open log file  failed, err:", err)
		return
	}
	log.SetOutput(logFile)
	log.SetFlags(log.Llongfile | log.Lmicroseconds | log.Ldate)
}


func Init(startTime string, machineID int64) (err error) {
	var st time.Time
	// 格式化 1月2号下午3时4分5秒  2006年
	st, err = time.Parse("2006-01-02", startTime)
	if err != nil {
		fmt.Println(err)
		return
	}
	snowflake.Epoch = st.UnixNano() / 1e6
	node, err = snowflake.NewNode(machineID)
	if err != nil {
		fmt.Println(err)
		return
	}
	return
}


// 生成 64 位的 雪花 ID
func GenID() int64 {
	return 	node.Generate().Int64()
}

// byte转int64
func byte2Int64(b []byte) int64 {
	buf := bytes.NewBuffer(b)
	var res int64
	binary.Read(buf, binary.BigEndian, &res)
	return res
}

// int64转byte
func int642Byte(num int64) []byte {
	buf := bytes.NewBuffer([]byte{})
	binary.Write(buf, binary.BigEndian, num)
	return buf.Bytes()
}


type message struct {
	Action string
	Data   map[string]string
}


//  客户端代理
type delegate struct{}


// 节点meta数据，可用于存放节点相关的客户数据；可通过Node结构体的Meta获取
func (d *delegate) NodeMeta(limit int) []byte {
  	return []byte{}
}

// memberlist收到userMsg信息后会调用该函数处理信息
func (d *delegate) NotifyMsg(b []byte) {
	if len(b) == 0 {
		return
	}
	switch b[0] {
	case 'd':
		var m message
		if err := json.Unmarshal(b[9:], &m); err != nil {
			return
		}
		messageID := byte2Int64(b[1: 9])
		if messages[messageID] > 0 {
			return
		}
		log.Printf("I receive a message called %d, now time is %d\n", messageID, time.Now().UnixNano())
		mtx.Lock()
		
		for k, v := range m.Data {
			switch m.Action {
			case "add":
				items[k] = v
			case "del":
				delete(items, k)
			}
		}
		mtx.Unlock()
		messages[messageID] = time.Now().Unix()
		broadcasts.QueueBroadcast(&broadcast{
			msg:    b,
			notify: nil,
		})
	}
  
}

func (d *delegate) GetBroadcasts(overhead, limit int) [][]byte {
  	return broadcasts.GetBroadcasts(overhead, limit)
}


// 由push/pull协程同步交换各自的items信息
func (d *delegate) LocalState(join bool) []byte {
	mtx.RLock()
	m := items
	mtx.RUnlock()
	b, _ := json.Marshal(m)
	return b
}

// PushPull协程将调用该函数同步节点状态
func (d *delegate) MergeRemoteState(buf []byte, join bool) {
	if len(buf) == 0 {
		return
	}
	var m map[string]string
	if err := json.Unmarshal(buf, &m); err != nil {
		fmt.Println(err.Error())
		return
	}
	mtx.Lock()
	for k, v := range m {
		items[k] = v
	}
	mtx.Unlock()
}

type broadcast struct {
	msg    []byte
	notify chan<- struct{}
}

func (b *broadcast) Invalidates(other mgossip.Broadcast) bool {
  	return false
}

func (b *broadcast) Message() []byte {
 	return b.msg
}

func (b *broadcast) Finished() {
	if b.notify != nil {
		close(b.notify)
	}
}

func addHandler(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	key := r.Form.Get("key")
	val := r.Form.Get("val")
	messageID := GenID()
	mtx.Lock()
	items[key] = val
	mtx.Unlock()
	b, err := json.Marshal(message{
		Action: "add",
		Data: map[string]string{
			key: val,
		},
	})
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	// 广播数据
	msg := append([]byte("d"), int642Byte(messageID)...)
	messages[messageID] = time.Now().Unix()
	log.Printf("I create a message called %d, now time %d, broadcast to others\n", messageID, time.Now().UnixNano())
	broadcasts.QueueBroadcast(&broadcast{
		msg:    append(msg, b...),
		notify: nil,
	})
}

func delHandler(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	key := r.Form.Get("key")
	//messageID := GenID()
	mtx.Lock()
	delete(items, key)
	mtx.Unlock()
	b, err := json.Marshal(message{
		Action: "del",
		Data: map[string]string{
			key: "",
		},
	})
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	messageID := GenID()
	msg := append([]byte("d"), int642Byte(messageID)...)
	messages[messageID] = time.Now().Unix()
	log.Printf("I create a message called %d, now time %d, broadcast to others\n", messageID, time.Now().UnixNano())
	broadcasts.QueueBroadcast(&broadcast{
		msg:    append(msg, b...),
		notify: nil,
	})
}

func getHandler(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	key := r.Form.Get("key")
	mtx.RLock()
	val := items[key]
	mtx.RUnlock()
	if _, err := w.Write([]byte(val)); err != nil {
		fmt.Printf("fail to write response, err: %s.\n", err)
	}
}

func start() error {
	c := mgossip.DefaultWANConfig()
	c.Delegate = &delegate{}
	c.BindPort = bindPort
	c.BindAddr = bindAddr
	c.AdvertiseAddr = advertiseAddr
	c.AdvertisePort = bindPort
	c.Neighbors = neighbors
	c.PushPullInterval = 0 // 禁用PushPull协程(即反熵传播)
	c.GossipNodes = *gossipNodes 
	c.UDPBufferSize = *UDPBufferSize
	c.RetransmitMult = *systemBroadcastMult
	c.ProbeInterval = time.Duration(*probeInterval) * time.Second
	c.Name = fmt.Sprintf("%s:%d", advertiseAddr, bindPort)
	// 创建 Gossip 网络
	m, err := mgossip.Create(c)
	if err != nil {
		return err
	}
	// 第一个节点没有 member，从第二个开始有 member
	if len(memberlistAddr) > 0 {
		_, err := m.Join([]string{fmt.Sprintf("%s:%d", memberlistAddr, memberlistPort)})
		if err != nil {
			return err
		}
	}
	broadcasts = &mgossip.TransmitLimitedQueue{
		NumNodes: func() int {
			return m.NumMembers()
		},
		RetransmitMult: *retransmitMult,
	}
	node := m.LocalNode()
	fmt.Printf("Local member %s:%d\n", node.Addr, node.Port)
	return nil
}

func main() {
	if err := Init("2021-12-03", 1); err != nil {
		fmt.Println("Init() failed, err = ", err)
		return
	}
	if err := start(); err != nil {
		panic(err)
	}
	http.HandleFunc("/add", addHandler)
	http.HandleFunc("/del", delHandler)
	http.HandleFunc("/get", getHandler)
	fmt.Printf("Listening on :%d\n", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), nil); err != nil {
		panic(err)
	}
}