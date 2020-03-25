package model;


import java.util.ArrayList;
import java.util.List;
import java.util.Random;

class Robot {
    private Random r = new Random();
    private int x, y, rows, cols, heading;
    static final int AMT_DIRECTIONS = 4;
    static final int NORTH = 3;
    static final int EAST = 2;
    static final int SOUTH = 1;
    static final int WEST = 0;

    Robot(int rows, int cols) {
        this.x = r.nextInt(rows);
        this.y = r.nextInt(cols);
        this.rows = rows;
        this.cols = cols;
        this.heading = pick();
    }

    void move() {
        int[] pos = forward(x, y, heading);
        x = pos[0];
        y = pos[1];
        heading = pick();
    }

    int[] forward(int x, int y, int h) {
        switch (h) {
            case NORTH:
                y--;
                break;
            case EAST:
                x++;
                break;
            case SOUTH:
                y++;
                break;
            case WEST:
                x--;
                break;
        }
        return new int[]{x, y, h};
    }


    List<int[]> possible(int x, int y) {
        List<int[]> possible = new ArrayList<>();
        for (int h = 0; h < AMT_DIRECTIONS; h++) {
            if (traversable(x, y, h)) possible.add(forward(x, y, h));
        }
        return possible;
    }

    int[] sensor() {
        double prob = r.nextDouble();
        List<int[]> surrounding = surrounding(x, y,1);
        List<int[]> surrounding2 = surrounding(x, y, 2);
        final double TRUE_LOCATION_PROB = 0.1;
        final double SURROUNDING_PROB = 0.05*surrounding.size();
        final double SURROUNDING2_PROB = 0.025*surrounding2.size();
        if (prob < TRUE_LOCATION_PROB) {
            return new int[]{x, y};
        }
        else if (prob < TRUE_LOCATION_PROB + SURROUNDING_PROB) {
            return surrounding.get(r.nextInt(surrounding.size()));
        }
        else if (prob < TRUE_LOCATION_PROB + SURROUNDING_PROB + SURROUNDING2_PROB) {
            return surrounding2.get(r.nextInt(surrounding2.size()));
        }
        return new int[]{-1, -1};
    }

    int[] location() {
        return new int[]{x, y, heading};
    }


    List<int[]> surrounding(int x, int y, int dist) {
        List<int[]> surrounding = new ArrayList<>();
        for (int j = -dist; j <= dist; j++) {
            for (int i = -dist; i <= dist; i++) {
                int sX = x + j;
                int sY = y + i;
                if (within(sX, sY) && (i != 0 || j != 0)     && shebyshev(x, sX, y, sY) == dist) {
                    int[] location = new int[]{sX, sY};
                    surrounding.add(location);
                }
            }
        }
        return surrounding;
    }

    private int shebyshev(int x1, int x2, int y1, int y2) {
        int y = Math.abs(y2 - y1);
        int x = Math.abs(x2 - x1);
        return Math.max(x, y);
    }


    private boolean within(int x, int y) {
        return x >= 0 && x < rows && y >= 0 && y < cols;
    }

    private int pick() {
        if (traversable(x, y, heading)) {
            double prob = r.nextDouble();
            if (prob < 0.7) return heading;
        }
        int h;
        do {
            h = r.nextInt(AMT_DIRECTIONS);
        } while (!traversable(x, y, h) || h == heading);

        return h;
    }

    boolean traversable(int x, int y, int h) {
        switch (h) {
            case NORTH:
                return within(x, y-1);
            case EAST:
                return within(x+1, y);
            case SOUTH:
                return within(x, y+1);
            case WEST:
                return within(x-1, y);
            default:
                return false;
        }
    }


}
