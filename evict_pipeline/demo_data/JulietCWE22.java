import java.io.File;

/**
 * Juliet-style Sample for CWE-22 (Path Traversal)
 */
public class JulietCWE22 {
    
    /**
     * Vulnerable Method (True Positive)
     * Directly uses user input to construct a file path.
     */
    public void bad(String input) {
        // EVICT should label this as TP
        File file = new File("/var/app/data/" + input);
        System.out.println("Processing file: " + file.getName());
    }

    /**
     * Safe Method (False Positive)
     * Uses a hardcoded file name, ignoring untrusted input.
     */
    public void good(String input) {
        // EVICT should label this as FP
        File file = new File("/var/app/data/default_config.txt");
        System.out.println("Processing file: " + file.getName());
    }
}
