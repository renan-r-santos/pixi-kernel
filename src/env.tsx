import { PageConfig } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { WidgetProps } from '@rjsf/utils';
import React, { useEffect, useState } from 'react';

import { requestAPI } from './handler';

interface IPixiEnvProps extends WidgetProps {
  nbTracker: INotebookTracker;
}

export const PixiEnvWidget = (props: IPixiEnvProps) => {
  const [envs, setEnvs] = useState(['']);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const relativePath = props.nbTracker?.currentWidget?.context.path || '';
        const serverRoot = PageConfig.getOption('serverRoot') || '';

        const environments = await requestAPI<string[]>('envs', {
          method: 'POST',
          body: JSON.stringify({ relativePath, serverRoot })
        });

        setEnvs(environments);
      } catch (error) {
        console.error('Failed to fetch environments:', error);
        setEnvs(['']);
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
      {envs.map(env => (
        <option key={env} value={env}>
          {env}
        </option>
      ))}
    </select>
  );
};
