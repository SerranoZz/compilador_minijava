class Otimizacao{
    public static void main(String[] a){
        System.out.println(new Exemplo1().Contas(2));
    }
}

class Exemplo1 {
    int num_aux1;
    int num_aux2;
    public int Contas(int num){
        num_aux1 = 5;
        num_aux2 = 3 * num_aux1;
        num_aux1 = num * 2;
        if (num_aux2 < 100) {
            num_aux1 = 22;
            num_aux1 = num_aux1 * 8;
        }
        else {
            num_aux1 = 5;
            num_aux1 = num_aux1 - 1;
        }
        return num_aux1;
    }
}