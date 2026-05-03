/**
 * Juliet-style Sample for CWE-78 (OS Command Injection)
 */
public class JulietCWE78 {
    
    /**
     * Vulnerable Method (True Positive)
     * Directly passes user input to a system command.
     */
    public void bad(String input) throws Exception {
        // EVICT should label this as TP
        Runtime.getRuntime().exec("ls " + input);
    }

    /**
     * Safe Method (False Positive)
     * Passes a hardcoded constant to the command, ignoring untrusted input.
     */
    public void good(String input) throws Exception {
        // EVICT should label this as FP
        Runtime.getRuntime().exec("ls /tmp/safe_dir");
    }
}
