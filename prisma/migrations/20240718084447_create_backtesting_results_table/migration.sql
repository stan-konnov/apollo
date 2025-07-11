-- CreateTable
CREATE TABLE "backtesting_results" (
    "id" TEXT NOT NULL,
    "ticker" TEXT NOT NULL,
    "strategy" TEXT NOT NULL,
    "frequency" TEXT NOT NULL,
    "parameters" JSONB NOT NULL,
    "start_date" TIMESTAMP(3),
    "end_date" TIMESTAMP(3),
    "max_period" BOOLEAN NOT NULL,
    "exposure_time" DOUBLE PRECISION NOT NULL,
    "total_return" DOUBLE PRECISION NOT NULL,
    "buy_and_hold_return" DOUBLE PRECISION NOT NULL,
    "annualized_return" DOUBLE PRECISION NOT NULL,
    "annualized_volatility" DOUBLE PRECISION NOT NULL,
    "sharpe_ratio" DOUBLE PRECISION NOT NULL,
    "sortino_ratio" DOUBLE PRECISION NOT NULL,
    "calmar_ratio" DOUBLE PRECISION NOT NULL,
    "max_drawdown" DOUBLE PRECISION NOT NULL,
    "average_drawdown" DOUBLE PRECISION NOT NULL,
    "max_drawdown_duration" TEXT NOT NULL,
    "average_drawdown_duration" TEXT NOT NULL,
    "number_of_trades" INTEGER NOT NULL,
    "win_rate" DOUBLE PRECISION NOT NULL,
    "best_trade" DOUBLE PRECISION NOT NULL,
    "worst_trade" DOUBLE PRECISION NOT NULL,
    "average_trade" DOUBLE PRECISION NOT NULL,
    "max_trade_duration" TEXT NOT NULL,
    "average_trade_duration" TEXT NOT NULL,
    "system_quality_number" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "backtesting_results_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "backtesting_results_id_key" ON "backtesting_results"("id");
