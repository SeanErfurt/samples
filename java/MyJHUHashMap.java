/** MyJHUHashMap
 *
 *      Implementation of a hash map, satisfying the JHUHashMap interface.
 *
 * @author Sean Erfurt, serfurt1@jhu.edu
 *
 */
import java.util.*;

public class MyJHUHashMap<K, V> implements JHUHashMap<K, V> {
    private static final int CAP = 11;
    private static final double FACTOR = 0.5;

    private static class MyHMNode<K, V> {

        private final K key;
        private V value;
        private boolean dead;

        public MyHMNode(K k, V v) {
            this.key = k;
            this.value = v;
            this.dead = false;
        }
    }

    private MyHMNode<K, V>[] table;
    private int cap;
    private final double factor;
    private int size;
    private K[] keys;

    // Constructors
    public MyJHUHashMap() {
        this.table = new MyJHUHashMap.MyHMNode[CAP];
        this.cap = CAP;
        this.factor = FACTOR;
        this.size = 0;
        this.keys = (K[]) new Object[CAP];
    }

    public MyJHUHashMap(int c, double f) {
        if (c < 0 || f <= 0 || f > 1) {
            throw new IllegalArgumentException();
        }
        this.table = new MyJHUHashMap.MyHMNode[c];
        this.cap = c;
        this.factor = f;
        this.size = 0;
        this.keys = (K[]) new Object[c];
    }

    // Methods
    /**
     * Associate the specified value with the specified key in this map. If the
     * map previously contained a mapping for the key, the old value is
     * replaced.
     */
    public V put(K key, V value) {
        // find the key
        int index = this.hash(key);
        MyHMNode<K, V> curr = this.table[index];
        // linear probing
        while (curr != null) { // while not empty
            if (curr.key.equals(key)) { // found
                if (!curr.dead) { // overwrite
                    V result = curr.value;
                    curr.value = value;
                    return result;
                } else {
                    // revive
                    break;
                }
            }
            curr = this.table[++index % (this.cap - 1)];
        }
        // unused spot
        this.table[index] = new MyHMNode<K, V>(key, value);
        this.keys[this.size++] = key; // register live key
        // check rehash condition
        if (this.size >= (this.factor * this.cap)) {
            // resize
            this.cap *= 2;
            MyHMNode<K, V>[] temp = new MyJHUHashMap.MyHMNode[this.cap];
            // rehash
            for (int k = 0; k < this.size; k++) { // active keys only
                int i = this.hash(this.keys[k]);
                MyHMNode<K, V> node = temp[i];
                // linear probing
                while (node != null) { // while not empty
                    node = temp[++i % (this.cap - 1)];
                }
                // empty spot
                V v = this.get(this.keys[k]);
                temp[i] = new MyHMNode<K, V>(this.keys[k], v);
            }
            this.table = temp; // replace table
            // double size of keys array
            this.keys = Arrays.copyOf(this.keys, this.keys.length * 2);
        }
        return null; // no prev value
    }

    /**
     * Return the unique value to which the specified key is mapped, or null if
     * this map contains no mapping for the key. (A return value of null does
     * not necessarily indicate that the map contains no mapping for the key, as
     * no-mapping-present case from the map-with-null-value case.)
     */
    public V get(Object key) {
        if (!this.containsKey(key)) {
            return null; // key is dead
        }
        // find associated value
        int index = this.hash(key);
        MyHMNode<K, V> curr = this.table[index];
        // linear probing
        while (curr != null) { // while not empty
            if (curr.key.equals(key) && !curr.dead) { // matching live keys
                return curr.value;
            }
            curr = this.table[++index % (this.cap - 1)];
        }
        return null; // not found
    }

    public boolean containsKey(Object key) {
        for (int k = 0; k < this.size; k++) {
            if (this.keys[k].equals(key)) {
                return true;
            }
        }
        return false;
    }

    public V remove(Object key) {
        if (!this.containsKey(key)) {
            return null; // key is dead
        }
        // find associated value
        int index = this.hash(key);
        MyHMNode<K, V> curr = this.table[index];
        // linear probing
        while (curr != null) { // while not empty
            if (curr.key.equals(key) && !curr.dead) {
                curr.dead = true; // kill
                // remove from active keys
                for (int i = 0; i < this.size; i++) {
                    if (this.keys[i] == key) {
                        K[] copy = (K[]) new Object[this.keys.length - 1];
                        // copy up to the found key
                        System.arraycopy(this.keys, 0, copy, 0, i);
                        // skip key and copy the rest
                        System.arraycopy(this.keys, i + 1, copy, i,
                                this.keys.length - i - 1);
                        this.keys = copy;
                        break;
                    }
                }
                this.size--;
                return curr.value;
            }
            curr = this.table[++index % (this.cap - 1)];
        }
        return null; // not found
    }

    public void clear() {
        this.table = new MyJHUHashMap.MyHMNode[this.cap];
        this.size = 0;
        this.keys = (K[]) new Object[this.cap];
    }

    public int size() {
        return this.size;
    }

    public Set<K> keySet() {
        HashSet<K> result = new HashSet<K>(Arrays.asList(this.keys));
        return result;
    }

    public Collection<V> values() {
        ArrayList<V> result = new ArrayList<V>();
        for (int k = 0; k < this.size; k++) { // active keys only
            result.add(this.get(this.keys[k])); // store the value
        }
        return result;
    }

    private int hash(Object key) {
        return Math.abs(key.hashCode() % (this.table.length - 1));
    }

    public static void main(String[] args) {

        MyJHUHashMap<String, Integer> hm = new MyJHUHashMap<String, Integer>();
        if (hm.size() == 0) {
            System.out.println("Keys: " + hm.keySet());
            System.out.println("Values: " + hm.values());
        }
        hm.put("A", 1);
        if (hm.containsKey("A")) {
            System.out.println("Value of A: " + hm.get("A"));
            System.out.println("Size: " + hm.size());
        }
        System.out.println("Keys: " + hm.keySet());
        System.out.println("Values: " + hm.values());
        hm.remove("A");
        System.out.println("After remove");
        System.out.println("Keys: " + hm.keySet());
        System.out.println("Values: " + hm.values());
        System.out.println("Size: " + hm.size());

        for (int i = 0; i < 14; i++) {
            Random r = new Random();
            String s = Integer.toString(r.nextInt(100));
            hm.put(s, Integer.valueOf(i));
            System.out.println("Step " + i + " Values: " + hm.values());
        }
        System.out.println("After loop");
        System.out.println("Size: " + hm.size());
        System.out.println("Keys: " + hm.keySet());
        System.out.println("Values: " + hm.values());

        hm.clear();
        System.out.println("After clear");
        if (hm.size() == 0) {
            System.out.println("Keys: " + hm.keySet());
            System.out.println("Values: " + hm.values());
        }

        hm = new MyJHUHashMap<String, Integer>(20, .75);
        try {
            hm = new MyJHUHashMap<String, Integer>(-1, FACTOR);
        } catch (IllegalArgumentException e) {
            System.out.println("Caught negative capacity");
        }
        try {
            hm = new MyJHUHashMap<String, Integer>(1, -1);
        } catch (IllegalArgumentException e) {
            System.out.println("Caught negative factor");
        }
        try {
            hm = new MyJHUHashMap<String, Integer>(1, 2);
        } catch (IllegalArgumentException e) {
            System.out.println("Caught excessive factor");
        }
    }
}