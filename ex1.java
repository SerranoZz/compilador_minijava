class Factorial {
    public static void main(String[] a) {
        System.out.println(new Fac().ComputeFac(10));
    }
}
// Comentário de uma linha
class Fac {
    public int ComputeFac(int num) {
        int num_aux;
        if (num < 1) // Ignorar essa parte
            num_aux = 1;
        else
            num_aux = num * (this.ComputeFac(num - 1));
        return num_aux;
    }
    /*
     * Comentário de várias linhas
     * Remover aqui
     */
}