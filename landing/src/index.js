import {
  loadMultipleJSON
} from "@ud-viz/utils_browser";
import * as widgetSPARQL from '@ud-viz/widget_sparql';
import * as widgetVersioning from '@ud-viz/widget_versioning';

const setColor = function (default_color, override_color = undefined) {
    if (override_color) return override_color;
    return default_color;
};

loadMultipleJSON([
        './assets/config/versioning_widget.json',
        './assets/config/sparql_versioning_server.json',
    ])
    .then((configs) => {
        const sparqlVersioningWidgetView =
            new widgetVersioning.SparqlVersioningQueryWindow(
                new widgetSPARQL.SparqlEndpointResponseProvider(
                    configs['sparql_versioning_server']
                ),
                configs['versioning_widget']
            );

        sparqlVersioningWidgetView.addEventListeners({
            mouseover: ({ event, datum, graphId }) => {
                // Add mouseover event listener to the nodes of the d3Graphs
                const node_value =
                    sparqlVersioningWidgetView.getNodesByIdGraphAndIdNode(
                        graphId,
                        datum.index
                    );

                if (node_value !== undefined) {
                    sparqlVersioningWidgetView.d3Graphs.forEach((d3Graph) => {
                        const index = d3Graph.data.nodes.findIndex(
                            (d) => d.id === node_value
                        );

                        const nodes = d3Graph.data.nodes.map((d) => Object.create(d));

                        if (nodes[index] !== undefined) {
                            event.target.style['stroke'] = setColor(
                                'green'
                            );
                            event.target.style['fill'] = setColor(
                                'green'
                            );
                        }                        

                        d3Graph.node_label
                            .filter((e, j) => {
                                return index == j;
                            })
                            .style('fill', 'green')
                            .style('opacity', '1');
                        d3Graph.link_label
                            .filter((e) => {
                                return index == e.source.index || index == e.target.index;
                            })
                            .style('fill', 'green')
                            .style('opacity', '1');
                    });
                }
            },
            mouseout: function ({ event, datum, graphId }) {
                // Add mouseout event listener to the nodes of the d3Graphs
                const node_value =
                    sparqlVersioningWidgetView.getNodesByIdGraphAndIdNode(
                        graphId,
                        datum.index
                    );

                if (node_value !== undefined) {
                    sparqlVersioningWidgetView.d3Graphs.forEach((d3Graph) => {
                        const index = d3Graph.data.nodes.findIndex(
                            (d) => d.id === node_value
                        );

                        const nodes = d3Graph.data.nodes.map((d) => Object.create(d));
                        if (nodes[index] !== undefined) {
                            event.target.style['stroke'] = setColor(
                                '#ddd',
                                '#111'
                            );
                            event.target.style['fill'] = setColor(
                                'white'
                            );
                        }

                        d3Graph.node_label
                            .filter((e, j) => {
                                return index == j;
                            })
                            .style('fill', 'lightgrey')
                            .style('opacity', '0.5');
                        d3Graph.link_label
                            .filter((e) => {
                                return (
                                    index == e.source.index ||
                                    index == e.target.index
                                );
                            })
                            .style('fill', 'lightgrey')
                            .style('opacity', '0.5');
                    });
                }
            },
            click: ({ event, datum, graphId }) => {
                // Add click event listener to the nodes of the d3Graphs
                console.log('clicked node data:', event, datum, graphId);
            },
        });

        sparqlVersioningWidgetView.domElement.classList.add(
            'widget_versioning'
        );

        // Add UI
        const uiDomElement = sparqlVersioningWidgetView.domElement;
        uiDomElement.classList.add('full_screen');
        document.getElementById('ud-viz').appendChild(uiDomElement);
    });
