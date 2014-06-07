#include <cassert>
#include <ctime>
#include <cstdlib>
#include <cstdio>
#include <vector>

typedef std::vector< int > iv_t;
typedef std::vector< iv_t > ivv_t;

class Graph {
public:
    ivv_t ivv;
    int numV, numE;

    Graph() : numV(0), numE(0) {
        //printf("kkkk\n");
    }

    void clear(void) {
        ivv.clear();
        numV = numE = 0;
    }

    void needVertex(int v) {
        iv_t x;

        while( int(ivv.size()) <= v ) {
            ivv.push_back( x );
            numV++;
        }
    }

    void addEdge(int from, int to) {
        needVertex(from);
        needVertex(to);
        ivv[ from ].push_back( to );
        ivv[ to ].push_back( from );
        numE++;
    }

    void display() {
        for (int i = 0; i < numV; i++) {
            printf("%d:", i);
            for (int j = 0; j < ivv[i].size(); j++) {
                printf(" %d", ivv[i][j]);
            }
            printf("\n");
        }
    }

    int maxdegree() {
        int maxdeg = 0;
        for (int i = 0; i < numV; i++) {
            int deg = ivv[i].size();
            if (deg > maxdeg) {
                maxdeg = deg;
            }
        }
        return maxdeg;
    }

    int ovconj() {
        int maxdeg = maxdegree();
        if (maxdeg >= numV / 2) {       // max 1 induced overfull subgraph
            return 'L';
        }
        if (maxdeg >= numV / 3) {       // max 3 induced overfull subgraphs
            return 'P';
        }
        return 'N';
    }

    int overfull() {
        int maxdeg = maxdegree();
        if (numE > maxdeg * (numV / 2)) {
            return 'Y';
        }
        return 'N';
    }

    void fulldisplay() {
        printf("-------------\n");
        display();
        printf("Delta(G)=%d\n", maxdegree());
        printf("OvConj(G)=%c\n", ovconj());
        printf("Overfull(G)=%c\n", overfull());
        printf("-------------\n");
    }
};

void graphCopy(Graph& ga, Graph& gr) {
    gr.clear();
    // reserva o numero de vertices
    gr.needVertex(ga.numV - 1);

    for (int i = 0; i < ga.numV; i++) {
        for (int j = 0; j < ga.ivv[i].size(); j++) {
            int k = ga.ivv[i][j];
            if (i > k) {
                gr.addEdge(i, k);
            }
        }
    }
}

void graphUnion(Graph& ga, Graph& gb, Graph& gr) {
    gr.clear();
    // reserva o numero de vertices
    gr.needVertex(ga.numV + gb.numV - 1);

    for (int i = 0; i < ga.numV; i++) {
        for (int j = 0; j < ga.ivv[i].size(); j++) {
            int k = ga.ivv[i][j];
            if (i > k) {
                gr.addEdge(i, k);
            }
        }
    }
    for (int i = 0; i < gb.numV; i++) {
        for (int j = 0; j < gb.ivv[i].size(); j++) {
            int k = gb.ivv[i][j];
            if (i > k) {
                gr.addEdge(i + ga.numV, k + gb.numV);
            }
        }
    }
}

void graphComplement(Graph& from, Graph& to) {
    bool am[from.numV][from.numV];

    to.clear();
    // reserva o numero de vertices
    to.needVertex(from.numV - 1);

    // zera a matriz de adj
    for (int i = 0; i < from.numV; i++) {
        for (int j = 0; j < i; j++) {
            am[i][j] = false;
        }
    }
    // marca as arestas na matriz
    for (int i = 0; i < from.numV; i++) {
        for (int j = 0; j < from.ivv[i].size(); j++) {
            int k = from.ivv[i][j];
            if (i > k) {
                am[i][k] = true;
            } else {
                am[k][i] = true;
            }
        }
    }
    // acrescenta arestas
    for (int i = 0; i < from.numV; i++) {
        for (int j = 0; j < i; j++) {
            if (!am[i][j]) {
                to.addEdge(i, j);
            }
        }
    }
}

void cographMake(int myseed, int ucsep, int iterations, Graph& gr) {
    #define MAXCOGRAPHS 10
    if (myseed == 0) {
        myseed = time(NULL);
    }
    srand(myseed);
    Graph gv[MAXCOGRAPHS];

    for (int i = 0; i < MAXCOGRAPHS; i++) {
        gv[i].needVertex(0);
    }

    int r = 0;
    int a = 0;
    int b = 0;
    for (int i = 0; i < iterations; i++) {
        b = rand() % MAXCOGRAPHS;
        int rv = -1;
        for (int j = 0; j < MAXCOGRAPHS; j++) {
            if (j == a || j == b) {
                continue;
            }
            if (rv == -1 || gv[j].numE < rv) {
                r = j;
                rv = gv[j].numE;
            }
        }
        //printf("aaaa\n");
        assert(r != a && r != b);
        int op = rand() % 101;
        if (op >= ucsep) {
        //printf("aaaa %d %d\n", a, r);
            graphComplement(gv[a], gv[r]);
            printf("C ");
        } else {
        //printf("aaaa %d %d %d\n", a, b, r);
            graphUnion(gv[a], gv[b], gv[r]);
            printf("U ");
        }
        a = r;
    }
    printf("\n");
    graphCopy(gv[r], gr);
}

int main(void) {
    Graph g, g2, g3;
    //g.addEdge(0, 1);
    //g.addEdge(1, 2);
    //g.display();

    //graphComplement(g, g2);

    g.needVertex(0);

    graphUnion(g, g, g2);
    graphUnion(g, g2, g3);
    graphComplement(g3, g);

    g.fulldisplay();

    graphComplement(g, g2);
    g2.fulldisplay();

    cographMake(0, 80, 15, g);
    g.fulldisplay();

    // falta descobrir se é subgrafo-overfull
    printf("%d\n", RAND_MAX);

    return 0;
}
