/*
  Warnings:

  - A unique constraint covering the columns `[id,ticker,status]` on the table `positions` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "positions_id_ticker_status_key" ON "positions"("id", "ticker", "status");
