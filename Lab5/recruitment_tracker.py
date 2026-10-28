import ast
import math
import operator
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE applicants (id INTEGER PRIMARY KEY, name TEXT, role TEXT, expected_salary INTEGER, status TEXT)")


def addApplicant(name, role, expected_salary, status="applied"):
    conn.execute(
        "INSERT INTO applicants (name, role, expected_salary, status) "
        "VALUES (?, ?, ?, ?)",
        (name, role, expected_salary, status),
    )
    conn.commit()


def parse_salary_rule(salary_rule):
    """Evaluate bounded arithmetic without executing Python code.

    Only numbers, parentheses, +, -, *, / and unary signs are accepted.
    Expressions are limited to 128 characters and intermediate results
    must be finite with an absolute value no greater than 10**12.
    """
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluate(node):
        """Walk only the explicitly allowed expression nodes."""
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            value = evaluate(node.operand)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = -evaluate(node.operand)
        else:
            raise ValueError("Only numeric arithmetic is allowed")
        if not math.isfinite(value) or abs(value) > 10**12:
            raise ValueError("Salary arithmetic exceeds the supported range")
        return value

    if not isinstance(salary_rule, str) or not 0 < len(salary_rule) <= 128:
        raise ValueError("Supply a salary expression of 1 to 128 characters")
    try:
        expression = ast.parse(salary_rule.strip(), mode="eval")
        return evaluate(expression.body)
    except (SyntaxError, ZeroDivisionError) as error:
        raise ValueError("Invalid salary arithmetic") from error


def shortlist(role, salary_rule):
    rows = conn.execute("SELECT name, expected_salary FROM applicants WHERE role = ?", (role,)).fetchall()
    limit = parse_salary_rule(salary_rule)
    total_seen = len(rows)   
    result = []
    for name, salary in rows:
        if salary <= limit:
            result.append(name)
    if result:
        return result


def updateStatus(applicant_id, status):
    conn.execute("UPDATE applicants SET status = ? WHERE id = ?", (status, applicant_id))
    conn.commit()

def exportReport(path):
    f = open(path, "w")
    for row in conn.execute("SELECT name, role, status FROM applicants"):
        f.write(",".join(row) + "\n")
    f.close()


def countByStatus(status):
    return conn.execute("SELECT COUNT(*) FROM applicants WHERE status = ?", (status,)).fetchone()[0]


def main():
    addApplicant("Nina", "analyst", 600000)
    addApplicant("Omar", "analyst", 750000, "interview")
    addApplicant("Priya", "developer", 900000)
    updateStatus(1, "interview")
    print(shortlist("analyst", "500000 + 150000"))
    exportReport("applicants_report.csv")
    print(countByStatus("interview"), "in interview")


main()
