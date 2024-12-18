class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac1().ComputeFac23(10, 10, true));
    }
}

class Fac1 {
    int [] alo1;
    public int ComputeFac11(int num11){
        int num_aux11;
    	num_aux11 = num11 * (this.ComputeFac11(num11-1));
        return num_aux11;
    }

    public int ComputeFac12(int num12){
        int num_aux12;
    	num_aux12 = num12 * (this.ComputeFac12(num12-1));
        return num_aux12;
    }
}

class Fac2 {
    int [] alo2;
    public int ComputeFac23(int num23){
        int num_aux23;
    	num_aux23 = num23 * (this.ComputeFac23(num23-1));
        return num_aux23;
    }

    public int ComputeFac24(int num24){
        int num_aux24;
        alo2 = 23;
    	num_aux24 = num24 * (this.ComputeFac24(num24-1));
        return num_aux24;
    }
}