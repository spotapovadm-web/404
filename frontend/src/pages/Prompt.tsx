import { Icon } from '@iconify-icon/react';
import { Button } from '@/components';
import { GenTestType } from '@/lib/enums';
import type { TestType } from '@/lib/types';
import { useRef, useState } from 'react';
import { onSendButton } from '@lib/callbacks';
import type { JSX } from 'react';

function Prompt() {
  const reqRef = useRef<HTMLInputElement>(null);
  const productRef = useRef<HTMLInputElement>(null);
  const testTypeRef = useRef<HTMLSelectElement>(null);

  const [answers, setAnswers] = useState<JSX.Element[]>([]);

  const addAnswer = (answer: JSX.Element) => {
    setAnswers(prev => [...prev, answer]);
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-bg text-fg">

      <div className="flex-1 flex items-center justify-center">
        <h2 className="text-3xl font-bold">TestOps Copilot</h2>
        {answers}
      </div>

      <div className="fixed bottom-0 left-0 w-full flex justify-center">
        <div className="w-full lg:w-[50%] bg-primary p-4 rounded-t-2xl flex flex-col gap-4 shadow-xl">

          <div className="w-full flex flex-row gap-3 items-center">
            <input
              ref={productRef}
              placeholder="Введите название продукта"
              className="flex-1 bg-gray-600/50 text-white p-3 rounded-xl outline-none"
            />

            <div className="flex items-center gap-2">
              <label htmlFor="test_type" className="text-sm font-medium">
                Тип Теста:
              </label>

              <select
                ref={testTypeRef}
                id="test_type"
                name="test_type"
                className="bg-secondary text-white px-3 py-2 rounded-xl"
              >
                {Object.entries(GenTestType).map(([value]) => (
                  <option key={value} value={value as TestType}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="w-full flex flex-row gap-3 items-center">
            <input
              ref={reqRef}
              placeholder="Введите требования к тест-кейсу"
              className="flex-1 bg-gray-600/50 text-white p-3 rounded-xl outline-none"
            />

            <Button onClick={async () => await onSendButton(reqRef, testTypeRef, productRef, addAnswer)} className="w-12 h-12 flex items-center justify-center rounded-xl hover:bg-accent/75 active:bg-accent/50 transition-colors">
              <Icon icon="mingcute:arrow-up-fill" className="text-bg rotate-90" />
            </Button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Prompt;