class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac2().ComputeFac(10)); //Fac2 não existe
    }
}
class Fac {
    int num_aux1;
    public int ComputeFac(int num){
        int num_aux1;
        if (num < 1)
            num_aux2 = 2 + 8; //Variável num_aux2 não foi declarada
        else
            num_aux1 = num * (this.ComputeFac(num-1, 7)); //2 parâmetros são passados na função
        return num_aux1;
    }

    public int ComputeFac(int num){ //Função ComputeFac já foi declarada
        num_aux1 = num * (this.ComputeFac(true)); //Parâmetro com tipo errado
        return num_aux1;
    }
}