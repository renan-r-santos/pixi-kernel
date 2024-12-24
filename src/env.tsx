import { PageConfig } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { WidgetProps } from '@rjsf/utils';
import React, { useEffect, useState } from 'react';

import { requestAPI } from './handler';

interface IPixiEnvProps extends WidgetProps {
  nbTracker: INotebookTracker;
}

export const PixiEnvWidget = (props: IPixiEnvProps) => {
  const [options, setOptions] = useState<string[]>(['']);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const relativePath = props.nbTracker?.currentWidget?.context.path || '';
        const serverRoot = PageConfig.getOption('serverRoot') || '';

        const environments = await requestAPI<string[]>('envs', {
          method: 'POST',
          body: JSON.stringify({
            relativePath: relativePath,
            serverRoot: serverRoot
          })
        });

        setOptions(environments);
      } catch (error) {
        console.error('Failed to initialize pixi-kernel plugin:', error);
        setOptions(['']);
      }
    };

    fetchEnvironments();
  }, [props.nbTracker]);

  return (
    <select
      id={props.id}
      className="form-control"
      value={props.value || ''}
      onChange={e => props.onChange(e.target.value)}
      required={props.required}
    >
      {options.map(option => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
};
