import { JupyterFrontEnd } from '@jupyterlab/application';
import { PageConfig } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { WidgetProps } from '@rjsf/utils';
import React, { useEffect, useState } from 'react';

import { requestAPI } from './handler';

interface IPixiEnvProps extends WidgetProps {
  app: JupyterFrontEnd;
  nbTracker: INotebookTracker;
}

interface IEnvOption {
  name: string;
  default: boolean;
}

export const PixiEnvWidget = (props: IPixiEnvProps) => {
  const [envs, setEnvs] = useState<IEnvOption[]>([]);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        /** Get the local file path without any drive prefix potentially added by other extensions
         * like jupyter-collaboration: https://github.com/renan-r-santos/pixi-kernel/issues/47
         */
        const relativePath = props.nbTracker?.currentWidget?.context.path || '';
        const localPath =
          props.app.serviceManager.contents.localPath(relativePath);
        const serverRoot = PageConfig.getOption('serverRoot') || '';

        const environments = await requestAPI<IEnvOption[]>('envs', {
          method: 'POST',
          body: JSON.stringify({ localPath, serverRoot })
        });

        setEnvs(environments);
        // Select the first env with default: true, fallback to "default", else first
        let defaultEnvironmentName = environments.find(e => e.default)?.name;
        if (!defaultEnvironmentName) {
          defaultEnvironmentName = environments.find(
            e => e.name === 'default'
          )?.name;
        }
        if (!defaultEnvironmentName && environments.length > 0) {
          defaultEnvironmentName = environments[0].name;
        }
        // Only set if not already set by parent
        if (!props.value && defaultEnvironmentName) {
          props.onChange(defaultEnvironmentName);
        }
      } catch (error) {
        console.error('Failed to fetch environments:', error);
        setEnvs([]);
        if (!props.value) {
          props.onChange('');
        }
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
        <option key={env.name} value={env.name}>
          {env.name}
        </option>
      ))}
    </select>
  );
};
