// Same smoke test with go-redis v9: PING, SET/GET, server version, RESP3, local and the free Cloud database.
// Never prints the URL. usage: see README (runs in the golang image).
package main

import (
	"context"
	"fmt"
	"os"
	"regexp"

	"github.com/redis/go-redis/v9"
)

func main() {
	ctx := context.Background()
	fmt.Println("go-redis", redis.Version())
	for _, t := range []struct{ name, url string }{{"local", "redis://127.0.0.1:16379"}, {"cloud-free", os.Getenv("REDIS_URL")}} {
		opt, err := redis.ParseURL(t.url)
		if err != nil {
			fmt.Println(t.name, "bad URL"); continue
		}
		c := redis.NewClient(opt)
		pong, err := c.Ping(ctx).Result()
		if err != nil {
			fmt.Println(t.name, "error:", err); continue
		}
		c.Set(ctx, "smoke:go", "ok", 60e9)
		get, _ := c.Get(ctx, "smoke:go").Result()
		info, _ := c.Info(ctx, "server").Result()
		hello, _ := c.Do(ctx, "HELLO").Result()
		proto := "?"
		if m, ok := hello.(map[interface{}]interface{}); ok {
			proto = fmt.Sprint(m["proto"])
		}
		fmt.Printf("%s: PING=%s GET=%s version=%s protocol=%s\n", t.name, pong, get, regexp.MustCompile(`redis_version:(\S+)`).FindStringSubmatch(info)[1], proto)
		c.Close()
	}
}
