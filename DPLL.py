import sys

debug = False


class DPLL:
    def __init__(self, filename) -> None:
        print('command python', ' '.join(sys.argv))

        # initialize the variables that'll be used throughout 
        self.unit_clause_heuristic = False
        self.literals_tracker = {}
        self.not_assigned = set()
        self.dpll_iterations = 1

        # get the cmd line arguments 
        cmd_args = sys.argv
        if cmd_args[-1] == "+UCH":
            self.unit_clause_heuristic = True
            self.forced_LL = cmd_args[2:-1]
        else:
            self.forced_LL = cmd_args[2:]

        self.current_model = {}
        for forced_literal in self.forced_LL:
            if forced_literal[0] == '-':
                self.current_model[forced_literal[1:]] = -1
            else:
                self.current_model[forced_literal] = 1

        # get info from the cnf files
        self.initialize_statements(filename)

        self.display_current_model()

        # here is where we run the algorithm recursivley 
        is_valid = self.run_dpll()
        
        # check to see if we fail or succeed 
        # send corresponding msg 
        if not is_valid:
            self.failed()
        else:
            self.succeeded()
    # assign values using the UCH
    def find_unit_clause_heuristic(self):
        for clause in self.clauses:
            unassigned_literals = [(lit, neg) for lit, neg in clause if self.current_model[lit] == 0]
            satisfied_literals = [
                (lit, neg) for lit, neg in clause
                if (self.current_model[lit] == 1 and neg == 0) or (self.current_model[lit] == -1 and neg == 1)
            ]

            if not satisfied_literals and len(unassigned_literals) == 1:
                lit, neg = unassigned_literals[0]
                if neg != 0:
                    self.current_model[lit] = -1
                else:
                    self.current_model[lit] = 1

                if self.is_assignment_valid(lit):
                    return True, lit
                else:
                    self.current_model[lit] = 0

        return False, None


    # reads input file and then returns list of clauses as a result  
    def initialize_statements(self, file_name):
        self.clauses = []

        with open(file_name, 'r') as cnf_input:
            for clause_line in cnf_input:
                clause = [
                    (lit[1:], 1) if lit.startswith('-') else (lit, 0)
                    for lit in clause_line.split()
                ]
                self.clauses.append(clause)

                for lit, neg in clause:
                    if lit not in self.literals_tracker:
                        self.literals_tracker[lit] = []
                    self.literals_tracker[lit].append(len(self.clauses) - 1)

                    if lit not in self.current_model:
                        self.current_model[lit] = 0
                        self.not_assigned.add(lit)

    # valid check
    def is_assignment_valid(self, check_literal):
        if debug:
            print("Curr Check")
            print(self.current_model)

        for idx in self.literals_tracker[check_literal]:
            clause = self.clauses[idx]
            for lit, neg in clause:
                if self.current_model[lit] == 0:
                    break
                elif (self.current_model[lit] == 1 and neg == 0) or (self.current_model[lit] == -1 and neg == 1):
                    break
            else:
                return False
        return True

    # if solution succeeds we print it out
    def succeeded(self):
        print("...\nsolution:")
        _ = [print(f"{variable}: {value}") for variable, value in self.current_model.items()]

        print("Satisfied (true) propositions only:")
        satisfied_props = ' '.join(var for var, val in self.current_model.items() if val == 1)
        print(satisfied_props)
        print(f'total DPLL iterations: {self.dpll_iterations}\nUCH={self.unit_clause_heuristic}')
        
    # if solution failes we print it out
    def failed(self):
            print("...")
            print("unsatisfiable")
            print(f"total DPLL calls: {self.dpll_iterations}")
    # following examples for instruction PDF
    def display_current_model(self):
            debug and print(self.current_model)
            print("model", print("model", self.current_model))

    # run algo recursivley 
    def run_dpll(self):
        if debug:
            print("UNASSIGNED", self.not_assigned)

        if not self.not_assigned:
            return True

        if self.unit_clause_heuristic:
            while True:
                is_assigned, literal = self.find_unit_clause_heuristic()
                if not is_assigned:
                    break
                self.not_assigned.remove(literal)

        if not self.not_assigned:
            return True

        current_literal = self.not_assigned.pop()
        if debug:
            print("curr lit", current_literal)

        for assignment in [1, -1]:
            self.current_model[current_literal] = assignment
            print(f"trying {current_literal}={'T' if assignment == 1 else 'F'}")
            self.display_current_model()

            if self.is_assignment_valid(current_literal):
                self.dpll_iterations += 1
                if self.run_dpll():
                    return True
                else:
                    print("backtracking")

        self.not_assigned.add(current_literal)
        return False


if __name__ == "__main__":
    fname = sys.argv[1]
    dpll = DPLL(fname)
