import { useEffect, useRef } from "react";
import { Icon } from "@iconify-icon/react";

function ValidationPopup({
  opened,
  validations,
  onClose,
}: {
  opened: boolean;
  validations: Record<string, any>;
  onClose: CallableFunction;
}) {
  const popupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return opened === true ? (
    <div
      ref={popupRef}
      className="absolute z-50 bg-black/70  flex flex-col gap-2 top-[50%] mt-5 left-0 rounded-2xl p-2"
    >
      {validations &&
        Object.keys(validations).map((key, index) => (
          <span key={index} className="flex gap-1 items-center">
            <p>{key}</p>
            {validations[key] !== true ? (
              <Icon
                className="text-red-400"
                icon="material-symbols:error-rounded"
                width={20}
              />
            ) : (
              <Icon className="text-green-400" icon="mdi:success" width={20} />
            )}
          </span>
        ))}
    </div>
  ) : null;
}

export default ValidationPopup;
