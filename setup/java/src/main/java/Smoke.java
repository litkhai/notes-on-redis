// Same smoke test with Jedis, plus client-side caching on the local server. Never prints the URL.
import redis.clients.jedis.*;
import redis.clients.jedis.csc.CacheConfig;

public class Smoke {
  public static void main(String[] args) {
    java.util.Properties pp = new java.util.Properties();
    try (var in = RedisClient.class.getResourceAsStream("/META-INF/maven/redis.clients/jedis/pom.properties")) { pp.load(in); } catch (Exception e) {}
    System.out.println("jedis " + pp.getProperty("version"));
    String[][] targets = {{"local", "redis://127.0.0.1:16379"}, {"cloud-free", System.getenv("REDIS_URL")}};
    for (String[] t : targets) {
      try (RedisClient c = RedisClient.create(t[1])) {
        c.setex("smoke:jedis", 60, "ok");
        String v = c.info("server").replaceAll("(?s).*redis_version:(\\S+).*", "$1");
        System.out.printf("%s: PING=%s GET=%s version=%s%n", t[0], c.ping(), c.get("smoke:jedis"), v);
      }
    }
    System.out.println("-- client-side caching (RESP3 + CacheConfig), local");
    DefaultJedisClientConfig cfg = DefaultJedisClientConfig.builder().protocol(RedisProtocol.RESP3).build();
    try (RedisClient admin = RedisClient.create("redis://127.0.0.1:16379");
         RedisClient cached = RedisClient.builder().hostAndPort(new HostAndPort("127.0.0.1", 16379)).clientConfig(cfg)
             .cacheConfig(CacheConfig.builder().maxSize(1000).build()).build()) {
      admin.set("csc:jedis", "Ann");
      long before = calls(admin);
      long t0 = System.nanoTime(); String first = cached.get("csc:jedis"); long t1 = System.nanoTime();
      String last = null; for (int i = 0; i < 1000; i++) last = cached.get("csc:jedis"); long t2 = System.nanoTime();
      System.out.printf("first GET %s %.2f ms; next 1000 GETs %s %.2f ms in total; GETs that reached the server: %d%n",
          first, (t1 - t0) / 1e6, last, (t2 - t1) / 1e6, calls(admin) - before);
      admin.set("csc:jedis", "Bea");
      try { Thread.sleep(50); } catch (InterruptedException e) {}
      long b2 = calls(admin);
      System.out.printf("after another client's SET: %s; reached the server: %d%n", cached.get("csc:jedis"), calls(admin) - b2);
    }
  }
  static long calls(RedisClient c) {
    String s = c.info("commandstats");
    java.util.regex.Matcher m = java.util.regex.Pattern.compile("cmdstat_get:calls=(\\d+)").matcher(s);
    return m.find() ? Long.parseLong(m.group(1)) : 0;
  }
}
