package model;

import control.EstimatorInterface;

import java.util.Arrays;
import java.util.List;
import java.util.Random;

public class Localizer implements EstimatorInterface {
    private int rows, cols, head;
    private double[][] transistions;
    private double[][] observations;
    private double[] nothing;
    private double[] positions;
    private Robot robot;
    private int correct = 0;
    private int iterations = 0;
    private int randomGuesses = 0;
    private int sensorGuesses = 0;

    public Localizer(int rows, int cols, int head) {
        this.rows = rows;
        this.cols = cols;
        this.head = head;
        this.transistions = new double[rows * cols * Robot.AMT_DIRECTIONS][rows * cols * Robot.AMT_DIRECTIONS];
        this.observations = new double[rows * cols * Robot.AMT_DIRECTIONS][rows * cols];
        this.nothing = new double[rows * cols];
        this.positions = new double[rows * cols];
        this.robot = new Robot(rows, cols);
        createTransistionMatrix();
        createObservationalMatrix();
    }

    @Override
    public int getNumRows() {
        return rows;
    }

    @Override
    public int getNumCols() {
        return cols;
    }

    @Override
    public int getNumHead() {
        return head;
    }

    @Override
    public void update() {
        robot.move();
        int[] pos = getCurrentReading();
        double[] newPos = new double[rows * cols];
        for (int x1 = 0; x1 < cols; x1++) {
            for (int y1 = 0; y1 < rows; y1++) {
                for (int h1 = 0; h1 < Robot.AMT_DIRECTIONS; h1++) {
                    for (int x2 = 0; x2 < cols; x2++) {
                        for (int y2 = 0; y2 < rows; y2++) {
                            for (int h2 = 0; h2 < Robot.AMT_DIRECTIONS; h2++) {
                                newPos[x2 + y2 * cols] += getOrXY(pos[0], pos[1], x2, y2, h2) *
                                        getTProb(x1, y1, h1, x2, y2, h2) * positions[x1 + y1 * cols];
                            }
                        }
                    }
                }
            }
        }
        double sum = Arrays.stream(newPos).sum();
        double max = 0;
        int index = -1;
        for (int i = 0; i < rows * cols; i++) {
            if (max < newPos[i]) {
                max = newPos[i];
                index = i;
            }
            positions[i] = newPos[i] / sum;
        }

        int x1 = index % cols;
        int y1 = index / cols;
        int[] p = getCurrentTrueState();
        int manhattan = manhattan(x1, p[0], y1, p[1]);
        Random r = new Random();
        iterations++;
        if (manhattan == 0) correct++;
        if (pos[0] == getCurrentTrueState()[0] && pos[1] == getCurrentTrueState()[1]) sensorGuesses++;
        if (r.nextInt(rows * cols) == index)  randomGuesses++;
        System.out.println("Correct guesses: " + correct + " of " + iterations + " Percentage: " + correct * 100 / iterations + " %");
        System.out.println("Correct sensor guesses: " + sensorGuesses + " of " + iterations + " Percentage: " + sensorGuesses * 100 / iterations + " %");
        System.out.println("Correct random guesses: " + randomGuesses + " of " + iterations + " Percentage: " + randomGuesses * 100 / iterations + " %");

    }

    private int manhattan(int x1, int x2, int y1, int y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    @Override
    public int[] getCurrentTrueState() {
        return robot.location();
    }

    @Override
    public int[] getCurrentReading() {
        return robot.sensor();
    }

    @Override
    public double getCurrentProb(int x, int y) {
        return positions[x + cols * y];
    }

    @Override
    public double getOrXY(int rX, int rY, int x, int y, int h) {
        if (rX == -1 || rY == -1) return nothing[x + y * cols];
        return observations[Robot.AMT_DIRECTIONS * x + Robot.AMT_DIRECTIONS * y * cols + h][rX + cols * rY];
    }

    @Override
    public double getTProb(int x, int y, int h, int nX, int nY, int nH) {
        return transistions[Robot.AMT_DIRECTIONS * x + y * cols * Robot.AMT_DIRECTIONS + h]
                [Robot.AMT_DIRECTIONS * nX + nY * cols * Robot.AMT_DIRECTIONS + nH];
    }

    private void createObservationalMatrix() {
        for (int x = 0; x < rows; x++) {
            for (int y = 0; y < rows; y++) {
                for (int h = 0; h < Robot.AMT_DIRECTIONS; h++) {
                    observations[Robot.AMT_DIRECTIONS * x + Robot.AMT_DIRECTIONS * y * cols + h][x + y * cols] = 0.1;
                }
                List<int[]> s1 = robot.surrounding(x, y, 1);
                List<int[]> s2 = robot.surrounding(x, y, 2);
                setObservationSurrounding(x, y, s1, 0.05);
                setObservationSurrounding(x, y, s2, 0.025);
                nothing[x + y * cols] = 1 - 0.1 - s1.size() * 0.05 - s2.size() * 0.025;
                positions[x + y * cols] = 1.0 / (rows * cols);
            }
        }
    }

    private void setObservationSurrounding(int x, int y, List<int[]> surrounding, double p) {
        for (int[] pos : surrounding) {
            for (int h = 0; h < Robot.AMT_DIRECTIONS; h++) {
                observations[Robot.AMT_DIRECTIONS * pos[0] + Robot.AMT_DIRECTIONS * pos[1] * cols + h][x + y * cols] = p;
            }
        }
    }


    private void createTransistionMatrix() {
        for (int x = 0; x < rows; x++) {
            for (int y = 0; y < cols; y++) {
                for (int h = 0; h < Robot.AMT_DIRECTIONS; h++) {
                    double prob = 1;
                    int amt = robot.possible(x, y).size();
                    if (robot.traversable(x, y, h)) {
                        int[] next = robot.forward(x, y, h);
                        transistions[Robot.AMT_DIRECTIONS * x + Robot.AMT_DIRECTIONS * y * cols + h]
                                [Robot.AMT_DIRECTIONS * next[0] + Robot.AMT_DIRECTIONS * next[1] * cols + h] = 0.7;
                        prob -= 0.7;
                        amt -= 1;
                    }
                    setTransistionOtherDirection(x, y, h, prob, amt);
                }
            }
        }
    }

    private void setTransistionOtherDirection(int x, int y, int h, double p, int amt) {
        for (int nH = 0; nH < Robot.AMT_DIRECTIONS; nH++) {
            if (nH != h && robot.traversable(x, y, nH)) {
                int[] next = robot.forward(x, y, nH);
                transistions[Robot.AMT_DIRECTIONS * x + y * cols * Robot.AMT_DIRECTIONS + h]
                        [Robot.AMT_DIRECTIONS * next[0] + next[1] * cols * Robot.AMT_DIRECTIONS + nH] = p / amt;
            }
        }
    }
}