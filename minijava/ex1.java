class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac().ComputeFac(10));
    }
}
class Fac {
    public int ComputeFac(int num){
        int num_aux;
        int x;
        num_aux = num_aux + 2;
        if (num < 1)
            num_aux = 2;
        else
            num_aux = num * (this.ComputeFac(num-1));
        return num_aux ;
    }
}
