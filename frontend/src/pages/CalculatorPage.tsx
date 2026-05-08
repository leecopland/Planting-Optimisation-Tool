import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useCalculator } from "@/hooks/useCalculator";
import { useFarmMap } from "@/hooks/useFarmMap";
import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";
import FarmMap from "@/components/calculator/FarmMap";
import "@/components/calculator/calculator.css";

export default function CalculatorPage() {
  const [farmId, setFarmId] = useState("");
  const { result, isLoading, hasSearched, error } = useCalculator(farmId);
  const { boundary, grid } = useFarmMap(result ? Number(farmId) : null);

  return (
    <div className="calc-view-container">
      <Helmet>
        <title>Sapling Calculator | Planting Optimisation Tool</title>
      </Helmet>

      <CalculatorHeader />

      <div className="calc-controls-wrapper">
        <CalculatorSearch onSearch={setFarmId} isLoading={isLoading} />
      </div>

      {error && (
        <div className="calc-error-message">
          <p>
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {hasSearched && result && (
        <div className="calc-results-layout">
          <CalculatorResult result={result} />
          <FarmMap
            boundary={boundary}
            grid={grid}
            optimalAngle={result.optimal_angle}
          />
        </div>
      )}
    </div>
  );
}
