/**
 * Juliet-style Sample for CWE-89 (SQL Injection)
 */
public class JulietCWE89 {
    
    /**
     * Vulnerable Method (True Positive)
     * Directly concatenates user input into a SQL query.
     */
    public void bad(String input) {
        // EVICT should label this as TP
        String query = "SELECT * FROM users WHERE id = '" + input + "'";
        execute(query);
    }

    /**
     * Safe Method (False Positive)
     * Uses a hardcoded constant, but might be flagged by naive analyzers.
     */
    public void good(String input) {
        // EVICT should label this as FP because it ignores 'input'
        String query = "SELECT * FROM users WHERE id = 'admin'";
        execute(query);
    }

    private void execute(String sql) {
        // Database execution logic
        System.out.println("Executing: " + sql);
    }
}
