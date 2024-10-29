-- CreateTable
CREATE TABLE "positions" (
    "id" TEXT NOT NULL,
    "ticker" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "strategy" TEXT,
    "direction" INTEGER,
    "limit_price" DOUBLE PRECISION,
    "entry_price" DOUBLE PRECISION,
    "entry_date" TIMESTAMP(3),
    "unit_size" DOUBLE PRECISION,
    "cash_size" DOUBLE PRECISION,
    "stop_loss" DOUBLE PRECISION,
    "take_profit" DOUBLE PRECISION,
    "exit_price" DOUBLE PRECISION,
    "exit_date" TIMESTAMP(3),
    "return" DOUBLE PRECISION,
    "profit_and_loss" DOUBLE PRECISION,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "positions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "positions_id_key" ON "positions"("id");
