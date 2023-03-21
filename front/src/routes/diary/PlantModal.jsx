import React from "react";
import ReactDOM from "react-dom";
import classes from "./Modal.module.scss";

const PlantModal = ({ onClose, children, onItemClick }) => {
  const handlePlantItemClick = (e) => {
    onItemClick(e.target.textContent);
  };
  return ReactDOM.createPortal(
    <div className={classes.modalOverlay} onClick={onClose}>
      <div
        className={classes.modalContent}
        onClick={(e) => e.stopPropagation()}
      >
        <h1 onClick={handlePlantItemClick}>전체보기</h1>
        {children
          .reduce((unique, item) => {
            if (!unique.some((u) => u.plant_name === item.plant_name)) {
              unique.push(item);
            }
            return unique;
          }, [])
          .map((item) => (
            <h1 key={item.id} onClick={handlePlantItemClick}>
              {item.plant_name}
            </h1>
          ))}
      </div>
    </div>,
    document.getElementById("modal-root")
  );
};

export default PlantModal;
