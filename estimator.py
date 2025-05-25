from manimlib import *
import numpy as np
import pandas as pd

fluct = 0
table = 0
EPSILON = 0.002

def get_table():
    return pd.to_numeric(pd.DataFrame(pd.read_json("tables.json"))[input("Enter subject name ")].dropna(), downcast="integer")

def EValue(plist: list, vlist: list):
    return sum([plist[i]*vlist[i] for i in range(len(plist))])

def standard_deviation(plist: list, vlist: list, mean, f = lambda x, mean: (x - mean)**2):
    return math.sqrt(sum([plist[i]*f(vlist[i], mean) for i in range(len(plist))]))

def bf(p, n, k):
    return np.float128(math.comb(n, k))*(p**k)*((1-p)**(n-k))

def wbd(n, k):
    distribution = np.array([bf(i*EPSILON, n, k) for i in range(int(1/EPSILON))])
    return  distribution / sum(distribution)

def bd(p, n):
    return [bf(p, n, i) for i in range(n+1)]

def bdsum(plist, n):
    bds = [np.array(bd(i/n, n))*plist[i] for i in range(n+1)]
    bds = list(zip(*bds))
    return [sum(bd)/sum(plist) for bd in bds]

def pseudodictify(List):
    return [[e,i] for i, e in enumerate(List)]

def inverse(dict):
    return {dict[i]:i for i in dict}

def condense(arr, t):
    chunks = [arr[i*t:(i+1)*t] for i in range((len(arr)+t+1)//t)]
    return [sum(chunk) for chunk in chunks]
#Not obsolete now, the whole discrete part is obsolete instead

#Way too many useless/ugly functions above, need to refactor later

class Estimator_Continuous(Scene):
    drag_to_pan = False

    def construct(self):
        print("WARNING: EVERY GRAPH ON SCREEN IS A PDF, NOT AN ACTUAL PROBABILITY DISTRIBUTION")
        global table

        table = get_table()
        successes = int(input("Enter total points gained over all tests "))
        trials = int(input("Enter maximum possible points over all tests "))
        table_size = len(table)
        default_scores_text = Text("Average given score:")
        default_scores = Text(f"""{table[math.floor(successes/trials*(table_size-1))]}-{table[math.ceil(successes/trials*(table_size-1))]}""")
        default_scores_text.to_edge(UP + LEFT)
        default_scores.next_to(default_scores_text, RIGHT)
        self.play(Write(default_scores_text))
        self.play(Write(default_scores))

        probabilities_distribution = wbd(trials, successes)
        condensed_pdistribution = condense(probabilities_distribution, int(1/EPSILON//(table_size-1)))
        print(probabilities_distribution[-2])
        print(condensed_pdistribution, sum(condensed_pdistribution))
        probability_axes = Axes((0,32),
                                (0,1),
                                height=3.5, 
                                width=5,
                                unit_size=0.2)
        probability_axes.add_coordinate_labels()
        probability_text = Text("Knowledge estimates", font_size = 28)
        probability_mean = sum([probabilities_distribution[i]*i*EPSILON*(table_size-1) for i in range(int(1/EPSILON))])
        probability_deviation = standard_deviation(probabilities_distribution, [i*EPSILON*(table_size-1) for i in range(int(1/EPSILON))], probability_mean)
        probability_perfect = condensed_pdistribution[-1]
        print(probability_deviation, probability_mean)
        probability_mean_text = Text(f"Mean: {table[math.floor(probability_mean)]:.2f}", font_size = 20)
        probability_deviation_text = Text(f"Standard deviation: {probability_deviation:.2f}", font_size = 20)
        probability_perfect_text = Text(f"Perfect chance: {probability_perfect*100:.2f}%", font_size = 20)
        probability_axes.to_corner(LEFT + DOWN)
        self.play(Write(probability_axes, lag_ratio=0.01, run_time=1))
        top_probabilities = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(condensed_pdistribution))), reverse=True)[:3]):
            print(e)
            top_probabilities.append(Text(f"Value N{i+1}: {table[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_probabilities[-1].next_to(probability_axes, UP)
                top_probabilities[-1].align_to(probability_axes, RIGHT)
            else:
                top_probabilities[-1].next_to(top_probabilities[-2], UP)
                top_probabilities[-1].align_to(top_probabilities[-2], RIGHT)
        probability_mean_text.next_to(probability_axes, UP)
        probability_mean_text.align_to(probability_axes, LEFT)
        probability_deviation_text.next_to(probability_mean_text, UP)
        probability_deviation_text.align_to(probability_mean_text, LEFT)
        probability_perfect_text.next_to(probability_deviation_text, UP)
        probability_perfect_text.align_to(probability_deviation_text, LEFT)
        probability_text.next_to(probability_perfect_text, UP)
        probability_text.align_to(probability_axes, RIGHT)
        probability_graph = probability_axes.get_graph(
            lambda x: probabilities_distribution[math.ceil(int(x/(table_size-1)*len(probabilities_distribution)))-1]/max(probabilities_distribution),
            use_smoothing=False,
            color=YELLOW,
            x_range=[0,table_size-1,EPSILON*(table_size-1)]
        )
        self.play(ShowCreation(probability_graph))
        self.play(Write(probability_text))
        self.add(probability_axes)
        self.play(Write(probability_mean_text))
        self.play(Write(probability_deviation_text))
        self.play(Write(probability_perfect_text))
        for e in top_probabilities:
            self.play(Write(e))

        final_axes = Axes((0,32), (0,1), height=3.5, width=5)
        final_estimates = bdsum(probabilities_distribution, len(probabilities_distribution)-1)
        condensed_fdistribution = condense(final_estimates, int(1/EPSILON//(table_size-1)))
        print(len(probabilities_distribution))
        print(len(final_estimates))
        final_graph = final_axes.get_graph(
            lambda x: final_estimates[math.ceil(x*len(final_estimates))-1]/max(final_estimates),
            use_smoothing=False,
            color=YELLOW,
            x_range=[0,1,EPSILON]
        )
        final_axes.add_coordinate_labels()
        final_text = Text("Actual results", font_size = 28)
        final_mean = sum([final_estimates[i]*i*EPSILON*(table_size-1) for i in range(int(1/EPSILON))])
        final_deviation = standard_deviation(final_estimates, [i*EPSILON*(table_size-1) for i in range(int(1/EPSILON))], final_mean)
        final_perfect = condensed_fdistribution[-2]
        print(final_deviation, final_mean)
        final_mean_text = Text(f"Mean: {table[math.floor(final_mean)]:.2f}", font_size = 20)
        final_deviation_text = Text(f"Standard deviation: {final_deviation:.2f}", font_size = 20)
        final_perfect_text = Text(f"Perfect chance: {final_perfect*100:.2f}%", font_size = 20)
        final_axes.to_corner(RIGHT + DOWN)
        self.play(Write(final_axes, lag_ratio=0.01, run_time=1))
        top_probabilities = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(condensed_fdistribution))), reverse=True)[:3]):
            print(e)
            top_probabilities.append(Text(f"Value N{i+1}: {table[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_probabilities[-1].next_to(final_axes, UP)
                top_probabilities[-1].align_to(final_axes, RIGHT)
            else:
                top_probabilities[-1].next_to(top_probabilities[-2], UP)
                top_probabilities[-1].align_to(top_probabilities[-2], RIGHT)
        final_mean_text.next_to(final_axes, UP)
        final_mean_text.align_to(final_axes, LEFT)
        final_deviation_text.next_to(final_mean_text, UP)
        final_deviation_text.align_to(final_mean_text, LEFT)
        final_perfect_text.next_to(final_deviation_text, UP)
        final_perfect_text.align_to(final_deviation_text, LEFT)
        final_text.next_to(final_perfect_text, UP)
        final_text.align_to(final_axes, RIGHT)
        final_graph = final_axes.get_graph(
            lambda x: final_estimates[math.ceil(int(x/(table_size-1)*len(final_estimates)))-1]/max(final_estimates),
            use_smoothing=False,
            color=YELLOW,
            x_range=[0,table_size-1,EPSILON*(table_size-1)]
        )
        self.play(ShowCreation(final_graph))
        self.play(Write(final_text))
        self.add(final_axes)
        self.play(Write(final_mean_text))
        self.play(Write(final_deviation_text))
        self.play(Write(final_perfect_text))
        for e in top_probabilities:
            self.play(Write(e))
        #self.add(final_graph)
        