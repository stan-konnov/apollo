/*
  Warnings:

  - The primary key for the `backtesting_results` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `backtesting_results` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "backtesting_results" DROP CONSTRAINT "backtesting_results_pkey",
DROP COLUMN "id",
ADD CONSTRAINT "backtesting_results_pkey" PRIMARY KEY ("ticker", "strategy", "frequency", "max_period");
